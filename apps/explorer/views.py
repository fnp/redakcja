from librarian import html
import hg, urllib2, json

from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.http import HttpResponseRedirect

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
            repo.add_file(path, form.cleaned_data['text'])
            # issues = _get_issues_for_file(path)
            # commit_message = _add_references(form.cleaned_data['commit_message'], issued)
            repo.commit(message=form.cleaned_data['commit_message'], user=form.cleaned_data['user'])
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = forms.BookForm()
        form.fields['text'].initial = repo.get_file(path).data()
    
    return direct_to_template(request, 'explorer/file_xml.html', extra_context={
        'hash': path,
        'form': form,
        'image_folders_form': forms.ImageFoldersForm(),
    })


def file_html(request, path):
    return direct_to_template(request, 'explorer/file_html.html', extra_context={
        'object': html.transform(repo.get_file(path).data(), is_file=False),
        'hash': path,
        'image_folders_form': forms.ImageFoldersForm(),
    })
  
def folder_images(request, folder):
    return direct_to_template(request, 'explorer/folder_images.html', extra_context={
        'images': models.get_images_from_folder(folder),
    })

def _add_references(message, issues):
    # TODO
    pass

def _get_issues_for_file(path):
    if not path.endswith('.xml'):
        raise ValueError('Path must end with .xml')

    book_id = path[:-3]
    uf = urllib2.urlopen(settings.REDMINE_URL + 'publications/%s/issues' % book_id)

    try:
        return json.loads(uf.read())
    finally:
        uf.close()
