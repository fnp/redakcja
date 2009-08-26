from librarian import html
import hg, urllib2, time
from django.utils import simplejson as json

from django.views.generic.simple import direct_to_template

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from explorer import forms, models

repo = hg.Repository(settings.REPOSITORY_PATH)

def file_list(request):
    return direct_to_template(request, 'explorer/file_list.html', extra_context={
        'objects': repo.all_files(),
    })


#
# Edit the file
#
def file_xml(request, path):
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            print 'Saving whole text.', request.user.username
            def save_action():
                repo.add_file(path, form.cleaned_data['content'])
                repo.commit(message='Local save at %s' % time.ctime(), user=request.user.username)

            repo.in_branch('local_'+request.user.username, save_action);
            return HttpResponse( json.dumps({'result': 'ok', 'errors': []}) );
    else:
        form = forms.BookForm()
        form.fields['content'].initial = repo.get_file(path).data()

    return direct_to_template(request, 'explorer/edit_text.html', extra_context={
        'form': form,
    })

def file_dc(request, path):
    return HttpResponse("N/A")

# Display the main editor view
def display_editor(request, path):
    return direct_to_template(request, 'explorer/editor.html', extra_context={
        'hash': path,
    })

# ===============
# = Panel views =
# ===============

def xmleditor_panel(request, path):
    form = forms.BookForm()
    text = repo.get_file(path).data()
    
    return direct_to_template(request, 'explorer/panels/xmleditor.html', extra_context={
        'fpath': path,
        'text': text,
    })
    

def gallery_panel(request, path):
    return direct_to_template(request, 'explorer/panels/gallery.html', extra_context={
        'fpath': path,
        'form': forms.ImageFoldersForm(),
    })


def htmleditor_panel(request, path):
    return direct_to_template(request, 'explorer/panels/htmleditor.html', extra_context={
        'fpath': path,
        'html': html.transform(repo.get_file(path).data(), is_file=False),
    })
 

def dceditor_panel(request, path):
    if request.method == 'POST':
        form = forms.DublinCoreForm(request.POST)
        if form.is_valid():
            form.save(repo, path)
            repo.commit(message='%s: DublinCore edited' % path)
    else:
        text = repo.get_file(path).data()
        form = forms.DublinCoreForm(text=text)       

    return direct_to_template(request, 'explorer/panels/dceditor.html', extra_context={
        'fpath': path,
        'form': form,
    })


# =================
# = Utility views =
# =================
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
