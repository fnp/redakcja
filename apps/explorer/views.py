from librarian import html
import hg, urllib2, time
from django.utils import simplejson as json

from django.views.generic.simple import direct_to_template

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

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
    return direct_to_template(request, 'explorer/file_list.html', extra_context={
        'objects': repo.all_files(),
    })
#
# Edit the file
#

@ajax_login_required
@with_repo
def file_xml(request, repo, path):
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            print 'Saving whole text.', request.user.username
            def save_action():
                print 'In branch: ' + repo.repo[None].branch()
                print repo._add_file(path, form.cleaned_data['content'])
                print repo.repo.status()
                print repo._commit(message=(form.cleaned_data['commit_message'] or 'Lokalny zapis platformy.'), user=request.user.username)

            print repo.in_branch(save_action, models.user_branch(request.user) );
            result = "ok"
        else:
            result = "error"

        errors = dict( (field[0], field[1].as_text()) for field in form.errors.iteritems() )
        return HttpResponse( json.dumps({'result': result, 'errors': errors}) );

    form = forms.BookForm()
    data = repo.get_file(path, models.user_branch(request.user))
    form.fields['content'].initial = data
    return HttpResponse( json.dumps({'result': 'ok', 'content': data}) ) 

@ajax_login_required
@with_repo
def file_dc(request, path, repo):
    if request.method == 'POST':
        form = forms.DublinCoreForm(request.POST)
        if form.is_valid():
            form.save(repo, path)
            result = "ok"
        else:
            result = "error" 

        errors = dict( (field[0], field[1].as_text()) for field in form.errors.iteritems() )
        return HttpResponse( json.dumps({'result': result, 'errors': errors}) );
    
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
    text = repo.get_file(path, user_branch)
    form = forms.DublinCoreForm(text=text)       

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
