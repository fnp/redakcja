# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import functools
import logging
logger = logging.getLogger("fnp.wiki_img")

from django.urls import reverse
from wiki.helpers import (JSONResponse, JSONFormInvalid, JSONServerError,
                ajax_require_permission)

from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
from django.utils.formats import localize
from django.utils.translation import gettext as _

from documents.models import Image
from wiki import forms
from wiki import nice_diff
from wiki_img.forms import ImageSaveForm

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache


@never_cache
def editor(request, slug, template_name='wiki_img/document_details.html'):
    doc = get_object_or_404(Image, slug=slug)

    return render(request, template_name, {
        'document': doc,
        'forms': {
            "text_save": ImageSaveForm(user=request.user, prefix="textsave"),
            "text_revert": forms.DocumentTextRevertForm(prefix="textrevert"),
            "pubmark": forms.DocumentPubmarkForm(prefix="pubmark"),
        },
        'can_pubmark': request.user.has_perm('documents.can_pubmark_image'),
        'REDMINE_URL': settings.REDMINE_URL,
    })


@require_GET
def editor_readonly(request, slug, template_name='wiki_img/document_details_readonly.html'):
    doc = get_object_or_404(Image, slug=slug)
    try:
        revision = request.GET['revision']
    except (KeyError):
        raise Http404

    return render(request, template_name, {
        'document': doc,
        'revision': revision,
        'readonly': True,
        'REDMINE_URL': settings.REDMINE_URL,
    })


@never_cache
def text(request, image_id):
    doc = get_object_or_404(Image, pk=image_id)
    if request.method == 'POST':
        form = ImageSaveForm(request.POST, user=request.user, prefix="textsave")
        if form.is_valid():
            if request.user.is_authenticated:
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
                    request.user.has_perm('documents.can_pubmark_image'))
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
def history(request, object_id):
    # TODO: pagination
    doc = get_object_or_404(Image, pk=object_id)
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
                "tag": ',\n'.join(str(tag) for tag in change.tags.all()),
            })
    return JSONResponse(changes)


@never_cache
@require_POST
def revert(request, object_id):
    form = forms.DocumentTextRevertForm(request.POST, prefix="textrevert")
    if form.is_valid():
        doc = get_object_or_404(Image, pk=object_id)
        if not doc.accessible(request):
            return HttpResponseForbidden("Not authorized.")

        revision = form.cleaned_data['revision']

        comment = form.cleaned_data['comment']
        comment += "\n#revert to %s" % revision

        if request.user.is_authenticated:
            author = request.user
        else:
            author = None

        before = doc.revision()
        logger.info("Reverting %s to %s", object_id, revision)
        doc.at_revision(revision).revert(author=author, description=comment)

        return JSONResponse({
            'text': doc.materialize() if before != doc.revision() else None,
            'meta': {},
            'revision': doc.revision(),
        })
    else:
        return JSONFormInvalid(form)


@never_cache
def diff(request, object_id):
    revA = int(request.GET.get('from', 0))
    revB = int(request.GET.get('to', 0))

    if revA > revB:
        revA, revB = revB, revA

    if revB == 0:
        revB = None

    doc = get_object_or_404(Image, pk=object_id)
    if not doc.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # allow diff from the beginning
    if revA:
        docA = doc.at_revision(revA).materialize()
    else:
        docA = ""
    docB = doc.at_revision(revB).materialize()

    return HttpResponse(nice_diff.html_diff_table(docA.splitlines(),
                                         docB.splitlines(), context=3))


@require_POST
@ajax_require_permission('documents.can_pubmark_image')
def pubmark(request, object_id):
    form = forms.DocumentPubmarkForm(request.POST, prefix="pubmark")
    if form.is_valid():
        doc = get_object_or_404(Image, pk=object_id)
        if not doc.accessible(request):
            return HttpResponseForbidden("Not authorized.")

        revision = form.cleaned_data['revision']
        publishable = form.cleaned_data['publishable']
        change = doc.at_revision(revision)
        if publishable != change.publishable:
            change.set_publishable(publishable)
            return JSONResponse({"message": _("Revision marked")})
        else:
            return JSONResponse({"message": _("Nothing changed")})
    else:
        return JSONFormInvalid(form)
