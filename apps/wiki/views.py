import os

from django.conf import settings

from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from wiki.helpers import JSONResponse, JSONFormInvalid, JSONServerError, ajax_require_permission
from django import http

from wiki.models import getstorage, DocumentNotFound
from wiki.forms import DocumentTextSaveForm, DocumentTagForm, DocumentCreateForm
from datetime import datetime
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

import wlapi

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

import logging
logger = logging.getLogger("fnp.peanut.api")

import nice_diff
import operator

MAX_LAST_DOCS = 10


@never_cache
def document_list(request, template_name='wiki/document_list.html'):
    # TODO: find a way to cache "Storage All"
    return direct_to_template(request, template_name, extra_context={
        'document_list': getstorage().all(),
        'last_docs': sorted(request.session.get("wiki_last_docs", {}).items(),
                        key=operator.itemgetter(1), reverse=True),
    })


@never_cache
def document_detail(request, name, template_name='wiki/document_details.html'):

    try:
        document = getstorage().get(name)
    except DocumentNotFound:
        return http.HttpResponseRedirect(reverse("wiki_create_missing", args=[name]))

    access_time = datetime.now()
    last_documents = request.session.get("wiki_last_docs", {})
    last_documents[name] = access_time

    if len(last_documents) > MAX_LAST_DOCS:
        oldest_key = min(last_documents, key=last_documents.__getitem__)
        del last_documents[oldest_key]
    request.session['wiki_last_docs'] = last_documents

    return direct_to_template(request, template_name, extra_context={
        'document': document,
        'document_name': document.name,
        'document_info': document.info,
        'document_meta': document.meta,
        'forms': {
            "text_save": DocumentTextSaveForm(prefix="textsave"),
            "add_tag": DocumentTagForm(prefix="addtag"),
        },
    })


def document_create_missing(request, name):
    storage = getstorage()

    if request.method == "POST":
        form = DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            doc = storage.create_document(
                id=form.cleaned_data['id'],
                text=form.cleaned_data['text'],
            )

            return http.HttpResponseRedirect(reverse("wiki_details", args=[doc.name]))
    else:
        form = DocumentCreateForm(initial={
                "id": name.replace(" ", "_"),
                "title": name.title(),
        })

    return direct_to_template(request, "wiki/document_create_missing.html", extra_context={
        "document_name": name,
        "form": form,
    })


@never_cache
def document_text(request, name):
    storage = getstorage()

    if request.method == 'POST':
        form = DocumentTextSaveForm(request.POST, prefix="textsave")

        if form.is_valid():
            revision = form.cleaned_data['parent_revision']

            document = storage.get_or_404(name, revision)
            document.text = form.cleaned_data['text']

            storage.put(document,
                author=form.cleaned_data['author'] or request.user.username,
                comment=form.cleaned_data['comment'],
                parent=revision,
            )

            document = storage.get(name)

            return JSONResponse({
                'text': document.plain_text if revision != document.revision else None,
                'meta': document.meta(),
                'revision': document.revision,
            })
        else:
            return JSONFormInvalid(form)
    else:
        revision = request.GET.get("revision", None)

        try:
            try:
                revision = revision and int(revision)
                logger.info("Fetching %s", revision)
                document = storage.get(name, revision)
            except ValueError:
                # treat as a tag
                logger.info("Fetching tag %s", revision)
                document = storage.get_by_tag(name, revision)
        except DocumentNotFound:
            raise http.Http404

        return JSONResponse({
            'text': document.plain_text,
            'meta': document.meta(),
            'revision': document.revision,
        })


@never_cache
def document_gallery(request, directory):
    try:
        base_url = ''.join((
                        smart_unicode(settings.MEDIA_URL),
                        smart_unicode(settings.FILEBROWSER_DIRECTORY),
                        smart_unicode(directory)))

        base_dir = os.path.join(
                    smart_unicode(settings.MEDIA_ROOT),
                    smart_unicode(settings.FILEBROWSER_DIRECTORY),
                    smart_unicode(directory))

        def map_to_url(filename):
            return "%s/%s" % (base_url, smart_unicode(filename))

        def is_image(filename):
            return os.path.splitext(f)[1].lower() in (u'.jpg', u'.jpeg', u'.png')

        images = [map_to_url(f) for f in map(smart_unicode, os.listdir(base_dir)) if is_image(f)]
        images.sort()
        return JSONResponse(images)
    except (IndexError, OSError) as e:
        logger.exception("Unable to fetch gallery")
        raise http.Http404


@never_cache
def document_diff(request, name):
    storage = getstorage()

    revA = int(request.GET.get('from', 0))
    revB = int(request.GET.get('to', 0))

    if revA > revB:
        revA, revB = revB, revA

    if revB == 0:
        revB = None

    docA = storage.get_or_404(name, int(revA))
    docB = storage.get_or_404(name, int(revB))

    return http.HttpResponse(nice_diff.html_diff_table(docA.plain_text.splitlines(),
                                         docB.plain_text.splitlines(), context=3))


@never_cache
def document_history(request, name):
    storage = getstorage()

    # TODO: pagination
    changesets = list(storage.history(name))

    return JSONResponse(changesets)


@require_POST
@ajax_require_permission('wiki.can_change_tags')
def document_add_tag(request, name):
    storage = getstorage()

    form = DocumentTagForm(request.POST, prefix="addtag")
    if form.is_valid():
        doc = storage.get_or_404(form.cleaned_data['id'])
        doc.add_tag(tag=form.cleaned_data['tag'],
                    revision=form.cleaned_data['revision'],
                    author=request.user.username)
        return JSONResponse({"message": _("Tag added")})
    else:
        return JSONFormInvalid(form)


@require_POST
@ajax_require_permission('wiki.can_publish')
def document_publish(request, name):
    storage = getstorage()
    document = storage.get_by_tag(name, "ready_to_publish")

    api = wlapi.WLAPI(**settings.WL_API_CONFIG)

    try:
        return JSONResponse({"result": api.publish_book(document)})
    except wlapi.APICallException, e:
        return JSONServerError({"message": str(e)})
