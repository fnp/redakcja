import os

from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, Http404
from django.utils import simplejson as json

from wiki.models import storage, Document, DocumentNotFound
from wiki.forms import DocumentForm

def document_list(request, template_name = 'wiki/document_list.html'):
    return direct_to_template(request, template_name, extra_context = {
        'document_list': storage.all(),
    })


def document_detail(request, name, template_name = 'wiki/document_details.html'):
    try:
        document = storage.get(name)
    except DocumentNotFound:
        document = Document(storage, name = name, text = '')


    if request.method == 'POST':
        form = DocumentForm(request.POST, instance = document)
        if form.is_valid():
            document = form.save()
            return HttpResponse(json.dumps({'text': document.plain_text(), 'meta': document.meta(), 'revision': document.revision()}))
        else:
            return HttpResponse(json.dumps({'errors': form.errors}))
    else:
        form = DocumentForm(instance = document)

    return direct_to_template(request, template_name, extra_context = {
        'document': document,
        'form': form,
    })


def document_gallery(request, directory):
    try:
        base_dir = os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY, directory)
        images = [u'%s%s%s/%s' % (settings.MEDIA_URL, settings.FILEBROWSER_DIRECTORY, directory, f) for f in os.listdir(base_dir) if os.path.splitext(f)[1].lower() in (u'.jpg', u'.jpeg', u'.png')]
        images.sort()
        return HttpResponse(json.dumps(images))
    except (IndexError, OSError), e:
        raise Http404
