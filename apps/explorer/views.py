# -*- coding: utf-8 -*-
import urllib2
import hg
from librarian import html, parser, dcparser, ParseError, ValidationError

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template

from explorer import forms, models
from toolbar import models as toolbar_models

#
# Some useful decorators
#
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
        return HttpResponse( json.dumps({'result': 'access_denied'}) );
    return view_with_auth

#
# View all files
#
@with_repo
def file_list(request, repo):
    paginator = Paginator( repo.file_list('default'), 100);
    bookform = forms.BookUploadForm()

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        files = paginator.page(page)
    except (EmptyPage, InvalidPage):
        files = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'explorer/file_list.html', extra_context={
        'files': files, 'page': page, 'bookform': bookform,
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

                def upload_action():
                    print 'Adding file: %s' % f.name
                    repo._add_file(f.name, decoded.encode('utf-8') )
                    repo._commit(
                        message="File %s uploaded from platform by %s" %\
                            (f.name, request.user.username), \
                        user=request.user.username \
                    )
                    
                    # end of upload

                repo.in_branch(upload_action, 'default')

                # if everything is ok, redirect to the editor
                return HttpResponseRedirect( reverse('editor_view',
                        kwargs={'path': f.name}) )

            except hg.RepositoryException, e:
                other_errors.append(u'Błąd repozytorium: ' + unicode(e) )
            except UnicodeDecodeError, e:
                other_errors.append(u'Niepoprawne kodowanie pliku: ' + e.reason \
                 + u'. Żądane kodowanie: ' + e.encoding)
        # invalid form

    # get
    form = forms.BookUploadForm()
    return direct_to_template(request, 'explorer/file_upload.html',
        extra_context = {'form' : form, 'other_errors': other_errors})
   
#
# Edit the file
#

@ajax_login_required
@with_repo
def file_xml(request, repo, path):
    if request.method == 'POST':
        errors = None
        form = forms.BookForm(request.POST)
        if form.is_valid():
            print 'Saving whole text.', request.user.username
            def save_action():
                print 'In branch: ' + repo.repo[None].branch()
                repo._add_file(path, form.cleaned_data['content'])                
                repo._commit(message=(form.cleaned_data['commit_message'] or 'Lokalny zapis platformy.'),\
                     user=request.user.username)
            try:
                # wczytaj dokument z ciągu znaków -> weryfikacja
                document = parser.WLDocument.from_string(form.cleaned_data['content'])

                #  save to user's branch
                repo.in_branch(save_action, models.user_branch(request.user) );
            except (ParseError, ValidationError), e:
                errors = [e.message]              

        if not errors:
            errors = dict( (field[0], field[1].as_text()) for field in form.errors.iteritems() )

        return HttpResponse(json.dumps({'result': errors and 'error' or 'ok', 'errors': errors}));

    form = forms.BookForm()
    data = repo.get_file(path, models.user_branch(request.user))
    form.fields['content'].initial = data
    return HttpResponse( json.dumps({'result': 'ok', 'content': data}) ) 

@ajax_login_required
@with_repo
def file_dc(request, path, repo):
    errors = None

    if request.method == 'POST':
        form = forms.DublinCoreForm(request.POST)
        
        if form.is_valid():
            def save_action():
                file_contents = repo._get_file(path)

                # wczytaj dokument z repozytorium
                document = parser.WLDocument.from_string(file_contents)                    
                document.book_info.update(form.cleaned_data)
                
                print "SAVING DC"

                # zapisz
                repo._write_file(path, document.serialize())
                repo._commit( \
                    message=(form.cleaned_data['commit_message'] or 'Lokalny zapis platformy.'), \
                    user=request.user.username )
                
            try:
                repo.in_branch(save_action, models.user_branch(request.user) )
            except (ParseError, ValidationError), e:
                errors = [e.message]

        if errors is None:
            errors = ["Pole '%s': %s\n" % (field[0], field[1].as_text()) for field in form.errors.iteritems()]

        return HttpResponse( json.dumps({'result': errors and 'error' or 'ok', 'errors': errors}) );
    
    # this is unused currently, but may come in handy 
    content = []
    
    try:
        fulltext = repo.get_file(path, models.user_branch(request.user))
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
    path = unicode(path).encode("utf-8")
    if not repo.file_exists(path, models.user_branch(request.user)):
        try:
            data = repo.get_file(path, 'default')
            print type(data)

            def new_file():
                repo._add_file(path, data)
                repo._commit(message='File import from default branch',
                    user=request.user.username)
                
            repo.in_branch(new_file, models.user_branch(request.user) )
        except hg.RepositoryException, e:
            return direct_to_templace(request, 'explorer/file_unavailble.html',\
                extra_context = { 'path': path, 'error': e })

    return direct_to_template(request, 'explorer/editor.html', extra_context={
        'hash': path,
        'panel_list': ['lewy', 'prawy'],
        'scriptlets': toolbar_models.Scriptlet.objects.all()
    })

# ===============
# = Panel views =
# ===============

@ajax_login_required
@with_repo
def xmleditor_panel(request, path, repo):
    form = forms.BookForm()
    text = repo.get_file(path, models.user_branch(request.user))
    
    return direct_to_template(request, 'explorer/panels/xmleditor.html', extra_context={
        'fpath': path,
        'text': text,
    })
    

@ajax_login_required
def gallery_panel(request, path):
    return direct_to_template(request, 'explorer/panels/gallery.html', extra_context={
        'fpath': path,
        'form': forms.ImageFoldersForm(),
    })

@ajax_login_required
@with_repo
def htmleditor_panel(request, path, repo):
    user_branch = models.user_branch(request.user)
    try:
        return direct_to_template(request, 'explorer/panels/htmleditor.html', extra_context={
            'fpath': path,
            'html': html.transform(repo.get_file(path, user_branch), is_file=False),
        })
    except (ParseError, ValidationError), e:
        return direct_to_template(request, 'explorer/panels/parse_error.html', extra_context={
            'fpath': path, 'exception_type': type(e).__name__, 'exception': e, 'panel_name': 'Edytor HTML'}) 

@ajax_login_required
@with_repo
def dceditor_panel(request, path, repo):
    user_branch = models.user_branch(request.user)

    try:
        doc_text = repo.get_file(path, user_branch)
        document = parser.WLDocument.from_string(doc_text)
        form = forms.DublinCoreForm(info=document.book_info)       
        return direct_to_template(request, 'explorer/panels/dceditor.html', extra_context={
            'fpath': path,
            'form': form,
        })
    except (ParseError, ValidationError), e:
        return direct_to_template(request, 'explorer/panels/parse_error.html', extra_context={
            'fpath': path, 'exception_type': type(e).__name__, 'exception': e, 
            'panel_name': 'Edytor DublinCore'}) 

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

def _get_issues_for_file(path):
    if not path.endswith('.xml'):
        raise ValueError('Path must end with .xml')

    book_id = path[:-4]
    uf = None

    try:
        uf = urllib2.urlopen(settings.REDMINE_URL + 'publications/issues/%s.json' % book_id)
        return json.loads(uf.read())
    except urllib2.HTTPError:
        return []
    finally:
        if uf: uf.close()


# =================
# = Pull requests =
# =================
def pull_requests(request):
    return direct_to_template(request, 'manager/pull_request.html', extra_context = {
        'objects': models.PullRequest.objects.all()} )
