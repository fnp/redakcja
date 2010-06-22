from django.conf import settings

from django import http

# Views
from django.views.generic.simple import direct_to_template

# Decorators
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache

# Models
from django.contrib.contenttypes.models import ContentType
from dvcs.models import Document
from dcmeta.models import Description

@never_cache
def document_list(request):
    return direct_to_template(request,
        'wiki/document_list.html', extra_context={
        'docs': Document.objects.all(),
    })


@never_cache
def editor(request, document_id, template_name='wiki/document_details.html'):

    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise http.Http404

    meta_data = Description.objects.get(object_id=document_id,
                                        content_type=ContentType.objects.get_for_model(doc))

    return direct_to_template(request, template_name, extra_context={
        'document': doc,
        'document_name': doc.name,
        'document_info': meta_data,
        'document_meta': meta_data,
#        'forms': {
#            "text_save": DocumentTextSaveForm(prefix="textsave"),
#            "add_tag": DocumentTagForm(prefix="addtag"),
#        },
    })
