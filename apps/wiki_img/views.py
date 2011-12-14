import os
import functools
import logging
logger = logging.getLogger("fnp.wiki_img")

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from wiki.helpers import JSONResponse
from django import http
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.conf import settings
from django.utils.formats import localize

from catalogue.models import Image
from wiki_img.forms import DocumentTextSaveForm

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache


@never_cache
def editor(request, slug, template_name='wiki_img/document_details.html'):
    doc = get_object_or_404(Image, slug=slug)

    return direct_to_template(request, template_name, extra_context={
        'document': doc,
        'forms': {
            "text_save": DocumentTextSaveForm(user=request.user, prefix="textsave"),
        },
        'REDMINE_URL': settings.REDMINE_URL,
    })


@require_GET
def editor_readonly(request, slug, template_name='wiki_img/document_details_readonly.html'):
    doc = get_object_or_404(Image, slug=slug)
    try:
        revision = request.GET['revision']
    except (KeyError):
        raise Http404



    return direct_to_template(request, template_name, extra_context={
        'document': doc,
        'revision': revision,
        'readonly': True,
        'REDMINE_URL': settings.REDMINE_URL,
    })


@never_cache
def text(request, image_id):
    doc = get_object_or_404(Image, pk=image_id)
    if request.method == 'POST':
        form = DocumentTextSaveForm(request.POST, user=request.user, prefix="textsave")
        if form.is_valid():
            if request.user.is_authenticated():
                author = request.user
            else:
                author = None
            text = form.cleaned_data['text']
            parent_revision = form.cleaned_data['parent_revision']
            if parent_revision is not None:
                parent = doc.at_revision(parent_revision)
            else:
                parent = None
            stage = form.cleaned_data['stage_completed']
            tags = [stage] if stage else []
            publishable = (form.cleaned_data['publishable'] and
                    request.user.has_perm('catalogue.can_pubmark'))
            doc.commit(author=author,
                       text=text,
                       parent=parent,
                       description=form.cleaned_data['comment'],
                       tags=tags,
                       author_name=form.cleaned_data['author_name'],
                       author_email=form.cleaned_data['author_email'],
                       publishable=publishable,
                       )
            revision = doc.revision()
            return JSONResponse({
                'text': doc.materialize() if parent_revision != revision else None,
                'meta': {},
                'revision': revision,
            })
        else:
            return JSONFormInvalid(form)
    else:
        revision = request.GET.get("revision", None)
        
        try:
            revision = int(revision)
        except (ValueError, TypeError):
            revision = doc.revision()

        if revision is not None:
            text = doc.at_revision(revision).materialize()
        else:
            text = ''

        return JSONResponse({
            'text': text,
            'meta': {},
            'revision': revision,
        })


@never_cache
def history(request, chunk_id):
    # TODO: pagination
    doc = get_object_or_404(Image, pk=chunk_id)
    if not doc.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    changes = []
    for change in doc.history().reverse():
        changes.append({
                "version": change.revision,
                "description": change.description,
                "author": change.author_str(),
                "date": localize(change.created_at),
                "publishable": _("Publishable") + "\n" if change.publishable else "",
                "tag": ',\n'.join(unicode(tag) for tag in change.tags.all()),
            })
    return JSONResponse(changes)
