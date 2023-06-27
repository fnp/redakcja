# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
import os
import logging
from time import mktime
from urllib.parse import quote

from django.apps import apps
from django.conf import settings
from django.urls import reverse
from django import http
from django.http import Http404, HttpResponseForbidden
from django.middleware.gzip import GZipMiddleware
from django.utils.decorators import decorator_from_middleware
from django.utils.formats import localize
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404, render
from sorl.thumbnail import get_thumbnail

from documents.models import Book, Chunk
from . import nice_diff
from wiki import forms
from wiki.helpers import (JSONResponse, JSONFormInvalid, JSONServerError,
                ajax_require_permission)
from wiki.models import Theme

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

logger = logging.getLogger("fnp.wiki")

MAX_LAST_DOCS = 10


@never_cache
def editor(request, slug, chunk=None, template_name='wiki/document_details.html'):
    try:
        chunk = Chunk.get(slug, chunk)
    except Chunk.MultipleObjectsReturned:
        # TODO: choice page
        raise Http404
    except Chunk.DoesNotExist:
        if chunk is None:
            try:
                book = Book.objects.get(slug=slug)
            except Book.DoesNotExist:
                return http.HttpResponseRedirect(reverse("documents_create_missing", args=[slug]))
        else:
            raise Http404
    if not chunk.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    access_time = datetime.now()
    last_books = request.session.get("wiki_last_books", {})
    last_books[reverse(editor, args=[chunk.book.slug, chunk.slug])] = {
        'time': mktime(access_time.timetuple()),
        'title': chunk.pretty_name(),
        }

    if len(last_books) > MAX_LAST_DOCS:
        oldest_key = min(last_books, key=lambda x: last_books[x]['time'])
        del last_books[oldest_key]
    request.session['wiki_last_books'] = last_books

    return render(request, template_name, {
        'chunk': chunk,
        'forms': {
            "text_save": forms.DocumentTextSaveForm(user=request.user, prefix="textsave"),
            "text_revert": forms.DocumentTextRevertForm(prefix="textrevert"),
            "pubmark": forms.DocumentPubmarkForm(prefix="pubmark"),
        },
        'can_pubmark': request.user.has_perm('documents.can_pubmark'),
        'REDMINE_URL': settings.REDMINE_URL,
    })


def editor_user_area(request):
    return render(request, 'wiki/editor-user-area.html', {
        'forms': {
            "text_save": forms.DocumentTextSaveForm(user=request.user, prefix="textsave"),
            "text_revert": forms.DocumentTextRevertForm(prefix="textrevert"),
            "pubmark": forms.DocumentPubmarkForm(prefix="pubmark"),
        },
        'can_pubmark': request.user.has_perm('documents.can_pubmark'),
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
        'time': mktime(access_time.timetuple()),
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
def text(request, chunk_id):
    doc = get_object_or_404(Chunk, pk=chunk_id)
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.method == 'POST':
        form = forms.DocumentTextSaveForm(request.POST, user=request.user, prefix="textsave")
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
                    request.user.has_perm('documents.can_pubmark'))
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
@require_POST
def revert(request, chunk_id):
    form = forms.DocumentTextRevertForm(request.POST, prefix="textrevert")
    if form.is_valid():
        doc = get_object_or_404(Chunk, pk=chunk_id)
        if not doc.book.accessible(request):
            return HttpResponseForbidden("Not authorized.")

        revision = form.cleaned_data['revision']

        comment = form.cleaned_data['comment']
        comment += "\n#revert to %s" % revision

        if request.user.is_authenticated:
            author = request.user
        else:
            author = None

        before = doc.revision()
        logger.info("Reverting %s to %s", chunk_id, revision)
        doc.at_revision(revision).revert(author=author, description=comment)

        return JSONResponse({
            'text': doc.materialize() if before != doc.revision() else None,
            'meta': {},
            'revision': doc.revision(),
        })
    else:
        return JSONFormInvalid(form)


@never_cache
def gallery(request, directory):
    try:
        base_url = ''.join((
                        settings.MEDIA_URL,
                        settings.IMAGE_DIR,
                        directory))

        base_dir = os.path.join(
                    settings.MEDIA_ROOT,
                    settings.IMAGE_DIR,
                    directory)

        def map_to_url(filename):
            return quote(("%s/%s" % (base_url, filename)))

        def is_image(filename):
            return os.path.splitext(filename)[1].lower() in (u'.jpg', u'.jpeg', u'.png')

        books = Book.objects.filter(gallery=directory)

        if not all(book.public for book in books) and not request.user.is_authenticated:
            return HttpResponseForbidden("Not authorized.")

        images = [
            {
                "url": map_to_url(f),
                "thumb": get_thumbnail(os.path.join(base_dir, f), '120x120').url
            } for f in sorted(os.listdir(base_dir)) if is_image(f)
        ]

        return JSONResponse(images)
    except (IndexError, OSError):
        logger.exception("Unable to fetch gallery")
        raise http.Http404


@never_cache
def diff(request, chunk_id):
    revA = int(request.GET.get('from', 0))
    revB = int(request.GET.get('to', 0))

    if revA > revB:
        revA, revB = revB, revA

    if revB == 0:
        revB = None

    doc = get_object_or_404(Chunk, pk=chunk_id)
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # allow diff from the beginning
    if revA:
        docA = doc.at_revision(revA).materialize()
    else:
        docA = ""
    docB = doc.at_revision(revB).materialize()

    return http.HttpResponse(nice_diff.html_diff_table(docA.splitlines(),
                                         docB.splitlines(), context=3))


@never_cache
def revision(request, chunk_id):
    doc = get_object_or_404(Chunk, pk=chunk_id)
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")
    Presence = apps.get_model('team', 'Presence')
    Presence.report(request.user, doc, request.GET.get('a') == 'true')
    return http.HttpResponse(str(doc.revision()))


@never_cache
def history(request, chunk_id):
    # TODO: pagination
    doc = get_object_or_404(Chunk, pk=chunk_id)
    if not doc.book.accessible(request):
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
                "published": _("Published") + ": " + \
                    localize(change.publish_log.order_by('-book_record__timestamp')[0].book_record.timestamp) \
                    if change.publish_log.exists() else "",
            })
    return JSONResponse(changes)


@require_POST
@ajax_require_permission('documents.can_pubmark')
def pubmark(request, chunk_id):
    form = forms.DocumentPubmarkForm(request.POST, prefix="pubmark")
    if form.is_valid():
        doc = get_object_or_404(Chunk, pk=chunk_id)
        if not doc.book.accessible(request):
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


def themes(request):
    prefix = request.GET.get('q', '')
    return http.HttpResponse('\n'.join([str(t) for t in Theme.objects.filter(name__istartswith=prefix)]))


def back(request):
    return render(request, 'wiki/back.html')
