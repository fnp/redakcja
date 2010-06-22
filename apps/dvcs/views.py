# Create your views here.
from django.views.generic.simple import direct_to_template
from django import http
from dvcs.models import Document

def document_list(request, template_name="dvcs/document_list.html"):
    return direct_to_template(request, template_name, {
        "documents": Document.objects.all(),
    })

def document_data(request, document_id, version=None):
    doc = Document.objects.get(pk=document_id)
    return http.HttpResponse(doc.materialize(version or None), content_type="text/plain")

def document_history(request, docid, template_name="dvcs/document_history.html"):
    document = Document.objects.get(pk=docid)
    return direct_to_template(request, template_name, {
        "document": document,
        "changes": document.history(),
    })

