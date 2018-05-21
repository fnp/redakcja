# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import os
import logging
import urllib

from django.conf import settings
from django import http
from django.http import HttpResponseForbidden
from django.middleware.gzip import GZipMiddleware
from django.utils.decorators import decorator_from_middleware
from django.utils.encoding import smart_unicode
from django.utils.formats import localize
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render

from catalogue.models import Document, Template, Category
from dvcs.models import Revision
import nice_diff
from wiki import forms
from wiki.helpers import JSONResponse, JSONFormInvalid

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

logger = logging.getLogger("fnp.wiki")

MAX_LAST_DOCS = 10


def get_history(document):
    revisions = []
    for i, revision in enumerate(document.history()):
        revisions.append({
            "version": i + 1,
            "description": revision.description,
            "author": escape(revision.author_str()),
            "date": localize(revision.created_at),
            "revision": revision.pk,
            "published": _("Published") + ": " +
            localize(revision.publish_log.order_by('-timestamp')[0].timestamp)
            if revision.publish_log.exists() else "",
        })
    return revisions


@never_cache
def editor(request, pk, template_name='wiki/bootstrap.html'):
    doc = get_object_or_404(Document, pk=pk, deleted=False)
    if not doc.can_edit(request.user):
        return HttpResponseForbidden("Not authorized.")

    save_form = forms.DocumentTextSaveForm(user=request.user, prefix="textsave")
    text = doc.materialize()
    revision = doc.revision
    history = get_history(doc)
    return render(request, template_name, {
        'serialized_document_data': json.dumps({
            'document': text,
            'document_id': doc.pk,
            'title': doc.meta().get('title', ''),
            'history': history,
            'version': len(history),
            'revision': revision.pk,
            'stage': doc.stage,
            'stage_name': doc.stage_name(),
            'assignment': doc.assigned_to.username if doc.assigned_to else None,
        }),
        'serialized_templates': json.dumps([
            {'id': t.id, 'name': t.name, 'content': t.content} for t in Template.objects.filter(is_partial=True)
        ]),
        'forms': {
            "text_save": save_form,
            "text_revert": forms.DocumentTextRevertForm(prefix="textrevert"),
            "text_publish": forms.DocumentTextPublishForm(prefix="textpublish"),
        },
        'tag_categories': Category.objects.all(),
        'pk': doc.pk,
    })


@never_cache
@decorator_from_middleware(GZipMiddleware)
def text(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id, deleted=False)

    if request.method == 'POST':
        if not doc.can_edit(request.user):
            return HttpResponseForbidden("Not authorized.")
        form = forms.DocumentTextSaveForm(request.POST, user=request.user, prefix="textsave")
        if form.is_valid():
            if request.user.is_authenticated():
                author = request.user
            else:
                author = None
            text = form.cleaned_data['text']
            # parent_revision = form.cleaned_data['parent_revision']
            # if parent_revision is not None:
            #     parent = doc.at_revision(parent_revision)
            # else:
            #     parent = None
            stage = form.cleaned_data['stage']
            try:
                doc.commit(
                    author=author,
                    text=text,
                    description=form.cleaned_data['comment'],
                    author_name=form.cleaned_data['author_name'],
                    author_email=form.cleaned_data['author_email'],
                )
                doc.set_stage(stage)
            except:
                from traceback import print_exc
                print_exc()
                raise
            return JSONResponse({
                'text': None,  # doc.materialize() if parent_revision != revision else None,
                'version': len(get_history(doc)),
                'stage': doc.stage,
                'stage_name': doc.stage_name(),
                'assignment': doc.assigned_to.username if doc.assigned_to else None
            })
        else:
            return JSONFormInvalid(form)
    else:
        revision = request.GET.get("revision", None)
        
        try:
            revision = int(revision)
        except (ValueError, TypeError):
            revision = doc.revision

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
@require_POST
def revert(request, doc_id):
    form = forms.DocumentTextRevertForm(request.POST, prefix="textrevert")
    if form.is_valid():
        doc = get_object_or_404(Document, pk=doc_id, deleted=False)
        if not doc.can_edit(request.user):
            return HttpResponseForbidden("Not authorized.")
        rev = get_object_or_404(Revision, pk=form.cleaned_data['revision'])

        comment = form.cleaned_data['comment']
        comment += "\n#revert to %s" % rev.pk

        if request.user.is_authenticated():
            author = request.user
        else:
            author = None

        # before = doc.revision
        logger.info("Reverting %s to %s", doc_id, rev.pk)

        doc.commit(
            author=author,
            text=rev.materialize(),
            description=comment,
            # author_name=form.cleaned_data['author_name'], #?
            # author_email=form.cleaned_data['author_email'], #?
        )

        return JSONResponse({
            'document': doc.materialize(),
            'version': len(get_history(doc)),
            'stage': doc.stage,
            'stage_name': doc.stage_name(),
            'assignment': doc.assigned_to.username if doc.assigned_to else None,
        })
    else:
        return JSONFormInvalid(form)


@never_cache
def gallery(request, directory):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("Not authorized.")

    try:
        base_url = ''.join((
                        smart_unicode(settings.MEDIA_URL),
                        smart_unicode(settings.IMAGE_DIR),
                        smart_unicode(directory)))

        base_dir = os.path.join(
                    smart_unicode(settings.MEDIA_ROOT),
                    smart_unicode(settings.IMAGE_DIR),
                    smart_unicode(directory))

        def map_to_url(filename):
            return urllib.quote("%s/%s" % (base_url, smart_unicode(filename)))

        def is_image(filename):
            return os.path.splitext(f)[1].lower() in (u'.jpg', u'.jpeg', u'.png')

        images = [map_to_url(f) for f in map(smart_unicode, os.listdir(base_dir)) if is_image(f)]
        images.sort()

        return JSONResponse(images)
    except (IndexError, OSError):
        logger.exception("Unable to fetch gallery")
        raise http.Http404


@never_cache
def diff(request, doc_id):
    revA = int(request.GET.get('from', 0))
    revB = int(request.GET.get('to', 0))

    if revA > revB:
        revA, revB = revB, revA

    if revB == 0:
        revB = None

    # TODO: check if revisions in line.

    doc = get_object_or_404(Document, pk=doc_id, deleted=False)

    # allow diff from the beginning
    if revA:
        docA = Revision.objects.get(pk=revA).materialize()
    else:
        docA = ""
    docB = Revision.objects.get(pk=revB).materialize()

    return http.HttpResponse(nice_diff.html_diff_table(docA.splitlines(), docB.splitlines(), context=3))


@never_cache
def history(request, doc_id):
    # TODO: pagination
    doc = get_object_or_404(Document, pk=doc_id, deleted=False)

    return JSONResponse(get_history(doc))
