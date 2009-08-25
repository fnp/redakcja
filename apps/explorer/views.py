from librarian import html
import hg, urllib2
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

def file_xml(request, path):
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            # save the changes to a local branch
#           repo.write_lock()
            print request.user
#            repo.switch_to_branch(request.user.name)           
#            repo.add_file(path, form.cleaned_data['text'])
            
            # add references to comment
            issues = _get_issues_for_file(path)
            commit_message = _add_references(form.cleaned_data['commit_message'], issues)
            print 'Commiting with: ' + commit_message

#            repo.commit(message=commit_message, user=form.cleaned_data['user'])
        return HttpResponse( json.dumps({'message': commit_message}) )
    else:
        form = forms.BookForm()
        form.fields['text'].initial = repo.get_file(path).data()
    
    return direct_to_template(request, 'explorer/file_xml.html', extra_context={
        'hash': path,
        'form': form,
        'image_folders_form': forms.ImageFoldersForm(),
    })


# ===============
# = Panel views =
# ===============
def xmleditor_panel(request, path):
    form = forms.BookForm()
    text = repo.get_file(path).data()
    
    return direct_to_template(request, 'explorer/panels/xmleditor.html', extra_context={
        'text': text,
    })
    

def gallery_panel(request, path):
    return direct_to_template(request, 'explorer/panels/gallery.html', extra_context={
        'form': forms.ImageFoldersForm(),
    })


def htmleditor_panel(request, path):
    return direct_to_template(request, 'explorer/panels/htmleditor.html', extra_context={
        'html': html.transform(repo.get_file(path).data(), is_file=False),
    })
 

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
