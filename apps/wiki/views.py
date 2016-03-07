from datetime import datetime
import json
import os
import logging
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from django import http
from django.http import Http404, HttpResponseForbidden
from django.middleware.gzip import GZipMiddleware
from django.utils.decorators import decorator_from_middleware
from django.utils.encoding import smart_unicode
from django.utils.formats import localize
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from catalogue.models import Document, Template
from dvcs.models import Revision
import nice_diff
from wiki import forms
from wiki.helpers import (JSONResponse, JSONFormInvalid, JSONServerError,
                ajax_require_permission)

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
                "author": revision.author_str(),
                "date": localize(revision.created_at),
                "published": "",
                "revision": revision.pk,
                "published": _("Published") + ": " + \
                    localize(revision.publish_log.order_by('-timestamp')[0].timestamp) \
                    if revision.publish_log.exists() else "",
            })
    return revisions


@never_cache
#@login_required
def editor(request, pk, chunk=None, template_name='wiki/bootstrap.html'):
    doc = get_object_or_404(Document, pk=pk, deleted=False)
    #~ if not doc.accessible(request):
        #~ return HttpResponseForbidden("Not authorized.")

    access_time = datetime.now()

    save_form = forms.DocumentTextSaveForm(user=request.user, prefix="textsave")
    try:
        version = int(request.GET.get('version', None))
    except:
        version = None
    if version:
        text = doc.at_revision(version).materialize()
    else:
        text = doc.materialize()
        revision = doc.revision
    history = get_history(doc)
    return render(request, template_name, {
        'serialized_document_data': json.dumps({
            'document': text,
            'document_id': doc.pk,
            'title': doc.meta().get('title', ''),
            'history': history,
            'version': len(history), #version or chunk.revision(),
            'revision': revision.pk,
            'stage': doc.stage,
            'assignment': str(doc.assigned_to),
        }),
        'serialized_templates': json.dumps([
            {'id': t.id, 'name': t.name, 'content': t.content} for t in Template.objects.filter(is_partial=True)
        ]),
        'forms': {
            "text_save": save_form,
            "text_revert": forms.DocumentTextRevertForm(prefix="textrevert"),
            "text_publish": forms.DocumentTextPublishForm(prefix="textpublish"),
        },
        'pk': doc.pk,
    })


@require_GET
def editor_readonly(request, slug, chunk=None, template_name='wiki/document_details_readonly.html'):
    try:
        chunk = Chunk.get(slug, chunk)
        revision = request.GET['revision']
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist, KeyError):
        raise Http404
    if not chunk.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    access_time = datetime.now()
    last_books = request.session.get("wiki_last_books", {})
    last_books[slug, chunk.slug] = {
        'time': access_time,
        'title': chunk.book.title,
        }

    if len(last_books) > MAX_LAST_DOCS:
        oldest_key = min(last_books, key=lambda x: last_books[x]['time'])
        del last_books[oldest_key]
    request.session['wiki_last_books'] = last_books

    return render(request, template_name, {
        'chunk': chunk,
        'revision': revision,
        'readonly': True,
        'REDMINE_URL': settings.REDMINE_URL,
    })


@never_cache
@decorator_from_middleware(GZipMiddleware)
def text(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id, deleted=False)
    #~ if not doc.book.accessible(request):
        #~ return HttpResponseForbidden("Not authorized.")

    if request.method == 'POST':
        form = forms.DocumentTextSaveForm(request.POST, user=request.user, prefix="textsave")
        if form.is_valid():
            if request.user.is_authenticated():
                author = request.user
            else:
                author = None
            text = form.cleaned_data['text']
            #~ parent_revision = form.cleaned_data['parent_revision']
            #~ if parent_revision is not None:
                #~ parent = doc.at_revision(parent_revision)
            #~ else:
                #~ parent = None
            stage = form.cleaned_data['stage']
            #~ tags = [stage] if stage else []
            #~ publishable = (form.cleaned_data['publishable'] and
                    #~ request.user.has_perm('catalogue.can_pubmark'))
            try:
                doc.commit(author=author,
                       text=text,
                       parent=False,
                       description=form.cleaned_data['comment'],
                       author_name=form.cleaned_data['author_name'],
                       author_email=form.cleaned_data['author_email'],
                       )
                doc.set_stage(stage)
            except:
                from traceback import print_exc
                print_exc()
                raise
            #revision = doc.revision()
            return JSONResponse({
                'text': None, #doc.materialize() if parent_revision != revision else None,
                #'version': revision,
                #'stage': doc.stage.name if doc.stage else None,
                'assignment': doc.assigned_to.username if doc.assigned_to else None
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
@require_POST
def revert(request, doc_id):
    form = forms.DocumentTextRevertForm(request.POST, prefix="textrevert")
    if form.is_valid():
        doc = get_object_or_404(Document, pk=doc_id, deleted=False)
        rev = get_object_or_404(Revision, pk=form.cleaned_data['revision'])

        comment = form.cleaned_data['comment']
        comment += "\n#revert to %s" % rev.pk

        if request.user.is_authenticated():
            author = request.user
        else:
            author = None

        #before = doc.revision
        logger.info("Reverting %s to %s", doc_id, rev.pk)

        doc.commit(author=author,
               text=rev.materialize(),
               parent=False, #?
               description=comment,
               #author_name=form.cleaned_data['author_name'], #?
               #author_email=form.cleaned_data['author_email'], #?
               )

        return JSONResponse({
            #'document': None, #doc.materialize() if before != doc.revision else None,
            #'version': doc.revision(),
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

    return http.HttpResponse(nice_diff.html_diff_table(docA.splitlines(),
                                         docB.splitlines(), context=3))


@never_cache
def revision(request, chunk_id):
    doc = get_object_or_404(Chunk, pk=chunk_id)
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")
    return http.HttpResponse(str(doc.revision()))


@never_cache
def history(request, doc_id):
    # TODO: pagination
    doc = get_object_or_404(Document, pk=doc_id, deleted=False)

    return JSONResponse(get_history(doc))
