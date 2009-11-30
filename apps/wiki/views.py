from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

from wiki.models import storage, Document, DocumentNotFound
from wiki.forms import DocumentForm


def document_list(request, template_name='wiki/document_list.html'):
    return direct_to_template(request, template_name, extra_context={
        'document_list': storage.all(),
    })


def document_detail(request, name, template_name='wiki/document_details.html'):
    try:
        document = storage.get(name)
    except DocumentNotFound:
        document = Document(storage, name=name, text='')
        
    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = DocumentForm(instance=document)
    
    return direct_to_template(request, template_name, extra_context={
        'document': document,
        'form': form,
    })
