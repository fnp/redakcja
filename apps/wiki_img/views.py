import os
import functools
import logging
logger = logging.getLogger("fnp.wiki")

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from wiki.helpers import JSONResponse
from django import http
from django.shortcuts import get_object_or_404
from django.conf import settings

from wiki_img.models import ImageDocument
from wiki_img.forms import DocumentTextSaveForm

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache


@never_cache
def editor(request, slug, template_name='wiki_img/document_details.html'):
    doc = get_object_or_404(ImageDocument, slug=slug)

    return direct_to_template(request, template_name, extra_context={
        'document': doc,
        'forms': {
            "text_save": DocumentTextSaveForm(prefix="textsave"),
        },
        'REDMINE_URL': settings.REDMINE_URL,
    })


@never_cache
def text(request, slug):
    if request.method == 'POST':
        form = DocumentTextSaveForm(request.POST, prefix="textsave")
        if form.is_valid():
            document = get_object_or_404(ImageDocument, slug=slug)
            commit = form.cleaned_data['parent_commit']

            comment = form.cleaned_data['comment']

            if request.user.is_authenticated():
                user = request.user
            else:
                user = None

            document.doc.commit(
                parent=commit,
                text=form.cleaned_data['text'],
                author=user,
                description=comment
            )

            return JSONResponse({
                'text': document.doc.materialize(),
                'revision': document.doc.change_set.count(),
            })
        else:
            return JSONFormInvalid(form)
    else:
        doc = get_object_or_404(ImageDocument, slug=slug).doc
        return JSONResponse({
            'text': doc.materialize(),
            'revision': doc.change_set.count(),
            'commit': doc.head.id,
        })

