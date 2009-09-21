# -*- coding: utf-8 -*-
import urllib2
import hg, re
from datetime import date

import librarian

from librarian import html, parser, dcparser
from librarian import ParseError, ValidationError

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from explorer import forms, models
from toolbar import models as toolbar_models

from django.forms.util import ErrorList

#
# Some useful decorators

def file_branch(fileid, user=None):
    parts = fileid.split('$')
    return ('personal_'+ user.username + '_' if user is not None else '') \
        + 'file_' + parts[0]

def file_path(fileid):
    return 'pub_'+fileid+'.xml'

def with_repo(view):
    """Open a repository for this view"""
    def view_with_repo(request, *args, **kwargs):          
        kwargs['repo'] = hg.Repository(settings.REPOSITORY_PATH)
        return view(request, *args, **kwargs)
    return view_with_repo

#
def ajax_login_required(view):
    """Similar ro @login_required, but instead of redirect, 
    just return some JSON stuff with error."""
    def view_with_auth(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view(request, *args, **kwargs)
        # not authenticated
        return HttpResponse( json.dumps({'result': 'access_denied', 'errors': ['Brak dostępu.']}) );
    return view_with_auth

#
# View all files
#
@with_repo
def file_list(request, repo):
    #
    latest_default = repo.get_branch_tip('default')

    fl = []
    for file in repo.repo[latest_default]:
        m = re.match(u'^pub_([^/]+).xml$', file.decode('utf-8'), re.UNICODE)
        if m is not None:
            fl.append(m.group(1))
            
    bookform = forms.BookUploadForm()

    return direct_to_template(request, 'explorer/file_list.html', extra_context={
        'files': fl, 'bookform': bookform,
    })

@permission_required('explorer.can_add_files')
@with_repo
def file_upload(request, repo):
    other_errors = []
    if request.method == 'POST':
        form = forms.BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # prepare the data
                f = request.FILES['file']
                decoded = f.read().decode('utf-8')
                fileid = form.cleaned_data['bookname'].lower()
                rpath = file_path(fileid)

                if form.cleaned_data['autoxml']:
                    decoded = librarian.wrap_text(decoded, unicode(date.today()) )
                
                def upload_action():
                    repo._add_file(rpath, decoded.encode('utf-8') )
                    repo._commit(message="File %s uploaded by user %s" % \
                        (rpath, request.user.username), user=request.user.username)

                repo.in_branch(upload_action, 'default')

                # if everything is ok, redirect to the editor
                return HttpResponseRedirect( reverse('editor_view',
                        kwargs={'path': fileid}) )

            except hg.RepositoryException, e:
                other_errors.append(u'Błąd repozytorium: ' + unicode(e) )
            #except UnicodeDecodeError, e:
            #    other_errors.append(u'Niepoprawne kodowanie pliku: ' + e.reason \
            #     + u'. Żądane kodowanie: ' + e.encoding)
        # invalid form

    # get
    form = forms.BookUploadForm()
    return direct_to_template(request, 'explorer/file_upload.html',\
        extra_context = {'form' : form, 'other_errors': other_errors})
   
#
# Edit the file
#

@ajax_login_required
@with_repo
def file_xml(request, repo, path):
    rpath = file_path(path)
    if request.method == 'POST':
        errors = None
        warnings = None
        form = forms.BookForm(request.POST)
        if form.is_valid():
            print 'Saving whole text.', request.user.username
            try:
                # encode it back to UTF-8, so we can put it into repo
                encoded_data = form.cleaned_data['content'].encode('utf-8')

                def save_action():                    
                    repo._add_file(rpath, encoded_data)
                    repo._commit(message=(form.cleaned_data['commit_message'] or 'Lokalny zapis platformy.'),\
                         user=request.user.username)

                try:
                    # wczytaj dokument z ciągu znaków -> weryfikacja
                    document = parser.WLDocument.from_string(form.cleaned_data['content'])
                except (ParseError, ValidationError), e:
                    warnings = [u'Niepoprawny dokument XML: ' + unicode(e.message)]

                #  save to user's branch
                repo.in_branch(save_action, file_branch(path, request.user) );
            except UnicodeDecodeError, e:
                errors = [u'Błąd kodowania danych przed zapisem: ' + unicode(e.message)]
            except hg.RepositoryException, e:
                errors = [u'Błąd repozytorium: ' + unicode(e.message)]            

        if not errors:
            errors = dict( (field[0], field[1].as_text()) for field in form.errors.iteritems() )

        return HttpResponse( json.dumps({'result': errors and 'error' or 'ok',
            'errors': errors, 'warnings': warnings}) );

    form = forms.BookForm()
    data = repo.get_file(rpath, file_branch(path, request.user))
    form.fields['content'].initial = data
    return HttpResponse( json.dumps({'result': 'ok', 'content': data}) )

@ajax_login_required
@with_repo
def file_update_local(request, path, repo):
    result = None
    errors = None
    
    wlock = repo.write_lock()
    try:
        tipA = repo.get_branch_tip('default')
        tipB = repo.get_branch_tip( file_branch(path, request.user) )

        nodeA = repo.getnode(tipA)
        nodeB = repo.getnode(tipB)
        
        # do some wild checks - see file_commit() for more info
        if (repo.common_ancestor(tipA, tipB) == nodeA) \
        or (nodeB in nodeA.parents()):
            result = 'nothing-to-do'
        else:
            # Case 2+
            repo.merge_revisions(tipB, tipA, \
                request.user.username, 'Personal branch update.')
            result = 'done'
    except hg.UncleanMerge, e:
        errors = [e.message]
        result = 'fatal-error'
    except hg.RepositoryException, e:
        errors = [e.message]
        result = 'fatal-error'
    finally:
        wlock.release()

    if result is None:
        raise Exception("Ouch, this shouldn't happen!")
    
    return HttpResponse( json.dumps({'result': result, 'errors': errors}) );

@ajax_login_required
@with_repo
def file_commit(request, path, repo):
    result = None
    errors = None
    local_modified = False
    if request.method == 'POST':
        form = forms.MergeForm(request.POST)

        if form.is_valid():           
            wlock = repo.write_lock()
            try:
                tipA = repo.get_branch_tip('default')
                tipB = repo.get_branch_tip( file_branch(path, request.user) )

                nodeA = repo.getnode(tipA)
                nodeB = repo.getnode(tipB)

                print repr(nodeA), repr(nodeB), repo.common_ancestor(tipA, tipB), repo.common_ancestor(tipB, tipA)

                if repo.common_ancestor(tipB, tipA) == nodeA:
                    # Case 1:
                    #         * tipB
                    #         |
                    #         * <- can also be here!
                    #        /|
                    #       / |
                    # tipA *  *
                    #      |  |
                    # The local branch has been recently updated,
                    # so we don't need to update yet again, but we need to
                    # merge down to default branch, even if there was
                    # no commit's since last update
                    repo.merge_revisions(tipA, tipB, \
                        request.user.username, form.cleaned_data['message'])
                    result = 'done'
                elif any( p.branch()==nodeB.branch() for p in nodeA.parents()):
                    # Case 2:
                    #
                    # tipA *  * tipB
                    #      |\ |
                    #      | \|
                    #      |  * 
                    #      |  |
                    # Default has no changes, to update from this branch
                    # since the last merge of local to default.
                    if nodeB not in nodeA.parents():
                        repo.merge_revisions(tipA, tipB, \
                            request.user.username, form.cleaned_data['message'])
                        result = 'done'
                    else:
                        result = 'nothing-to-do'
                elif repo.common_ancestor(tipA, tipB) == nodeB:
                    # Case 3:
                    # tipA * 
                    #      |
                    #      * <- this case overlaps with previos one
                    #      |\
                    #      | \
                    #      |  * tipB
                    #      |  |
                    #
                    # There was a recent merge to the defaul branch and
                    # no changes to local branch recently.
                    # 
                    # Use the fact, that user is prepared to see changes, to
                    # update his branch if there are any
                    if nodeB not in nodeA.parents():
                        repo.merge_revisions(tipB, tipA, \
                            request.user.username, 'Personal branch update during merge.')
                        local_modified = True
                        result = 'done'
                    else:
                        result = 'nothing-to-do'
                else:
                    # both branches have changes made to them, so
                    # first do an update
                    repo.merge_revisions(tipB, tipA, \
                        request.user.username, 'Personal branch update during merge.')

                    local_modified = True

                    # fetch the new tip
                    tipB = repo.get_branch_tip( file_branch(path, request.user) )

                    # and merge back to the default
                    repo.merge_revisions(tipA, tipB, \
                        request.user.username, form.cleaned_data['message'])
                    result = 'done'
            except hg.UncleanMerge, e:
                errors = [e.message]
                result = 'fatal-error'
            except hg.RepositoryException, e:
                errors = [e.message]
                result = 'fatal-error'
            finally:
                wlock.release()
                
        if result is None:
            errors = [ form.errors['message'].as_text() ]
            if len(errors) > 0:
                result = 'fatal-error'

        return HttpResponse( json.dumps({'result': result, 'errors': errors, 'localmodified': local_modified}) );

    return HttpResponse( json.dumps({'result': 'fatal-error', 'errors': ['No data posted']}) )
    

@ajax_login_required
@with_repo
def file_dc(request, path, repo):
    errors = None
    rpath = file_path(path)

    if request.method == 'POST':
        form = forms.DublinCoreForm(request.POST)
        
        if form.is_valid():
            
            def save_action():
                file_contents = repo._get_file(rpath)

                # wczytaj dokument z repozytorium
                document = parser.WLDocument.from_string(file_contents)                    
                document.book_info.update(form.cleaned_data)             

                # zapisz
                repo._write_file(rpath, document.serialize().encode('utf-8'))
                repo._commit( \
                    message=(form.cleaned_data['commit_message'] or 'Lokalny zapis platformy.'), \
                    user=request.user.username )
                
            try:
                repo.in_branch(save_action, file_branch(path, request.user) )
            except UnicodeEncodeError, e:
                errors = ['Bład wewnętrzny: nie można zakodować pliku do utf-8']
            except (ParseError, ValidationError), e:
                errors = [e.message]

        if errors is None:
            errors = ["Pole '%s': %s\n" % (field[0], field[1].as_text()) for field in form.errors.iteritems()]

        return HttpResponse( json.dumps({'result': errors and 'error' or 'ok', 'errors': errors}) );
    
    # this is unused currently, but may come in handy 
    content = []
    
    try:
        fulltext = repo.get_file(rpath, file_branch(path, request.user))
        bookinfo = dcparser.BookInfo.from_string(fulltext)
        content = bookinfo.to_dict()
    except (ParseError, ValidationError), e:
        errors = [e.message]

    return HttpResponse( json.dumps({'result': errors and 'error' or 'ok', 
        'errors': errors, 'content': content }) ) 

# Display the main editor view

@login_required
@with_repo
def display_editor(request, path, repo):    

    # this is the only entry point where we create an autobranch for the user
    # if it doesn't exists. All other views SHOULD fail.
    def ensure_branch_exists():
        parent = repo.get_branch_tip('default')
        repo._create_branch(file_branch(path, request.user), parent)
        
    try:
        repo.with_wlock(ensure_branch_exists)
        
        return direct_to_template(request, 'explorer/editor.html', extra_context={
            'fileid': path,
            'panel_list': ['lewy', 'prawy'],
            'availble_panels': models.EditorPanel.objects.all(),
            'scriptlets': toolbar_models.Scriptlet.objects.all()
        })
    except KeyError:
        return direct_to_template(request, 'explorer/nofile.html', \
            extra_context = { 'fileid': path })

# ===============
# = Panel views =
# ===============
class panel_view(object):

    def __new__(cls, request, name, path, **kwargs):
    #try:        
        panel = models.EditorPanel.objects.get(id=name)
        method = getattr(cls, name + '_panel', None)
        if not panel or method is None:
            raise HttpResponseNotFound

        extra_context = method(request, path, panel, **kwargs)

        if not isinstance(extra_context, dict):
            return extra_context

        extra_context.update({
            'toolbar_groups': panel.toolbar_groups.all(),
            'toolbar_extra_group': panel.toolbar_extra,
            'fileid': path
        })

        return direct_to_template(request, 'explorer/panels/'+name+'.html',\
            extra_context=extra_context)

    @staticmethod
    @ajax_login_required
    @with_repo
    def xmleditor_panel(request, path, panel, repo):
        rpath = file_path(path)
        return {'text': repo.get_file(rpath, file_branch(path, request.user))}

    @staticmethod
    @ajax_login_required
    def gallery_panel(request, path, panel):
        return {'form': forms.ImageFoldersForm() }

    @staticmethod
    @ajax_login_required
    @with_repo
    def htmleditor_panel(request, path, panel, repo):
        rpath = file_path(path)
        user_branch = file_branch(path, request.user)
        try:
            result = html.transform(repo.get_file(rpath, user_branch), is_file=False)
            print "HTML: %r" % result
            return {'html': result}
        except (ParseError, ValidationError), e:
            return direct_to_template(request, 'explorer/panels/parse_error.html', extra_context={
            'fileid': path, 'exception_type': type(e).__name__, 'exception': e,
            'panel_name': panel.display_name})

    @staticmethod
    @ajax_login_required
    @with_repo
    def dceditor_panel(request, path, panel, repo):
        user_branch = file_branch(path, request.user)
        rpath = file_path(path)
        try:
            doc_text = repo.get_file(rpath, user_branch)
            document = parser.WLDocument.from_string(doc_text)
            form = forms.DublinCoreForm(info=document.book_info)
            return {'form': form}
        except (ParseError, ValidationError), e:
            return direct_to_template(request, 'explorer/panels/parse_error.html', extra_context={
            'fileid': path, 'exception_type': type(e).__name__, 'exception': e,
            'panel_name': panel.display_name})

##
## Editor "commands" and "dialogs"
##
@login_required
@with_repo
def print_html(request, path, repo):
    user_branch = file_branch(path, request.user)
    rpath = file_path(path)
    return HttpResponse( 
        html.transform(repo.get_file(rpath, user_branch), is_file=False),
        mimetype="text/html")

@login_required
@with_repo
def print_xml(request, path, repo):
    user_branch = file_branch(path, request.user)
    rpath = file_path(path)
    return HttpResponse( repo.get_file(rpath, user_branch), mimetype="text/plain; charset=utf-8")

@permission_required('explorer.can_add_files')
def split_text(request, path):
    rpath = file_path(path)
    valid = False    
    if request.method == "POST":
        sform = forms.SplitForm(request.POST, prefix='splitform')
        dcform = forms.DublinCoreForm(request.POST, prefix='dcform')

        print "validating sform"
        if sform.is_valid():
            valid = True
            if sform.cleaned_data['autoxml']:
                print "validating dcform"                
                valid = dcform.is_valid()        

        print "valid is ", valid
        if valid:
            uri = path + '$' + sform.cleaned_data['partname']
            child_rpath = file_path(uri)
            repo = hg.Repository(settings.REPOSITORY_PATH)            

            # save the text into parent's branch
            def split_action():
                if repo._file_exists(child_rpath):
                    el = sform._errors.get('partname', ErrorList())
                    el.append("Part with this name already exists")
                    sform._errors['partname'] = el
                    return False
                                        
                fulltext = sform.cleaned_data['fulltext']               
                fulltext = fulltext.replace(u'<include-tag-placeholder />',
                    librarian.xinclude_forURI('wlrepo://'+uri) )               

                repo._write_file(rpath, fulltext.encode('utf-8'))

                newtext = sform.cleaned_data['splittext']
                if sform.cleaned_data['autoxml']:
                    # this is a horrible hack - really
                    bi = dcparser.BookInfo.from_element(librarian.DEFAULT_BOOKINFO.to_etree())
                    bi.update(dcform.cleaned_data)

                    newtext = librarian.wrap_text(newtext, \
                        unicode(date.today()), bookinfo=bi )

                repo._add_file(child_rpath, newtext.encode('utf-8'))                
                repo._commit(message="Split from '%s' to '%s'" % (path, uri), \
                    user=request.user.username )
                return True

            if repo.in_branch(split_action, file_branch(path, request.user)):
                # redirect to success
                return HttpResponseRedirect( reverse('split-success',\
                    kwargs={'path': path})+'?child='+uri)
    else:
        try: # to read the current DC
            repo = hg.Repository(settings.REPOSITORY_PATH)
            fulltext = repo.get_file(rpath, file_branch(path, request.user))
            bookinfo = dcparser.BookInfo.from_string(fulltext)
        except (ParseError, ValidationError):
            bookinfo = librarian.DEFAULT_BOOKINFO

        sform = forms.SplitForm(prefix='splitform')
        dcform = forms.DublinCoreForm(prefix='dcform', info=bookinfo)
   
    return direct_to_template(request, 'explorer/split.html', extra_context={
        'splitform': sform, 'dcform': dcform, 'fileid': path} )

def split_success(request, path):
    return direct_to_template(request, 'explorer/split_success.html',\
        extra_context={'fileid': path, 'cfileid': request.GET['child']} )


# =================
# = Utility views =
# =================
@ajax_login_required
def folder_images(request, folder):
    return direct_to_template(request, 'explorer/folder_images.html', extra_context={
        'images': models.get_images_from_folder(folder),
    })

def _add_references(message, issues):
    return message + " - " + ", ".join(map(lambda issue: "Refs #%d" % issue['id'], issues))

def _get_issues_for_file(fileid):
    uf = None
    try:
        uf = urllib2.urlopen(settings.REDMINE_URL + 'publications/issues/%s.json' % fileid)
        return json.loads(uf.read())
    except urllib2.HTTPError:
        return []
    finally:
        if uf: uf.close()

# =================
# = Pull requests =
# =================
#def pull_requests(request):
#    return direct_to_template(request, 'manager/pull_request.html', extra_context = {
#        'objects': models.PullRequest.objects.all()} )
