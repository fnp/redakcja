# -*- coding: utf-8 -*-
from librarian import html
import hg, urllib2, time

from django.utils import simplejson as json

from librarian import dcparser, parser
from librarian import ParseError, ValidationError

from django.views.generic.simple import direct_to_template

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.contrib.auth.decorators import login_required, permission_required

from explorer import forms, models

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
    form = forms.BookUploadForm(request.POST, request.FILES)
    if form.is_valid():
        f = request.FILES['file']        

        def upload_action():
            print 'Adding file: %s' % f.name
            repo._add_file(f.name, f.read().decode('utf-8'))
            repo._commit(message="File %s uploaded from platform by %s" %
                (f.name, request.user.username), user=request.user.username)

        repo.in_branch(upload_action, 'default')
        return HttpResponseRedirect( reverse('editor_view', kwargs={'path': f.name}) )

    return direct_to_template(request, 'explorer/file_upload.html',
        extra_context = {'form' : form} )
   
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
    if request.method == 'POST':
        form = forms.DublinCoreForm(request.POST)
        errors = None
        
        if form.is_valid():
            def save_action():
                file_contents = repo._get_file(path)

                # wczytaj dokument z repozytorium
                document = parser.WLDocument.from_string(file_contents)

                rdf_ns = dcparser.BookInfo.RDF
                dc_ns = dcparser.BookInfo.DC

                rdf_attrs = {rdf_ns('about'): form.cleaned_data.pop('about')}
                field_dict = {}
                    
                for key, value in form.cleaned_data.items():
                    field_dict[ dc_ns(key) ] = value if isinstance(value, list) else [value]

                print field_dict

                new_info = dcparser.BookInfo(rdf_attrs, field_dict)
                document.book_info = new_info

                print "SAVING DC"

                    # zapisz
                repo._add_file(path, document.serialize())
                repo._commit( \
                    message=(form.cleaned_data['commit_message'] or 'Lokalny zapis platformy.'), \
                    user=request.user.username )
                
            try:
                repo.in_branch(save_action, models.user_branch(request.user) )
            except (ParseError, ValidationError), e:
                errors = [e.message]

        if errors is None:
            errors = dict( (field[0], field[1].as_text()) for field in form.errors.iteritems() )

        return HttpResponse( json.dumps({'result': errors and 'error' or 'ok', 'errors': errors}) );
    
    fulltext = repo.get_file(path, models.user_branch(request.user))
    form = forms.DublinCoreForm(text=fulltext)       
    return HttpResponse( json.dumps({'result': 'ok', 'content': fulltext}) ) 

# Display the main editor view

@login_required
def display_editor(request, path):
    return direct_to_template(request, 'explorer/editor.html', extra_context={
        'hash': path, 'panel_list': ['lewy', 'prawy'],
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
    return direct_to_template(request, 'explorer/panels/htmleditor.html', extra_context={
        'fpath': path,
        'html': html.transform(repo.get_file(path, user_branch), is_file=False),
    })
 

@ajax_login_required
@with_repo
def dceditor_panel(request, path, repo):
    user_branch = models.user_branch(request.user)
    doc_text = repo.get_file(path, user_branch)

    document = parser.WLDocument.from_string(doc_text)
    form = forms.DublinCoreForm(info=document.book_info)       

    return direct_to_template(request, 'explorer/panels/dceditor.html', extra_context={
        'fpath': path,
        'form': form,
    })


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
