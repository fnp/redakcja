from librarian import html
import hg

from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.http import HttpResponseRedirect

from explorer import forms


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
            repo.commit()
            return HttpResponseRedirect('/')
    else:
        form = forms.BookForm()
        form.fields['text'].initial = repo.get_file(path).data()
    
    return direct_to_template(request, 'explorer/file_xml.html', extra_context={
        'hash': path,
        'form': form,
    })


def file_html(request, path):
    return direct_to_template(request, 'explorer/file_html.html', extra_context={
        'object': html.transform(repo.get_file(path).data(), is_file=False),
        'hash': path,
    })
    