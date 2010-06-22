# Create your views here.
from django.views.generic.simple import direct_to_template
from dvcs.models import Document

def document_list(request, template_name="dvcs/document_list.html"):
    return direct_to_template(request, template_name, {
        "documents": Document.objects.all(),
    })

def document_history(request, docid, template_name="dvcs/document_history.html"):
    document = Document.objects.get(pk=docid)
    return direct_to_template(request, template_name, {
        "document": document,
        "changes": document.history(),
    })

