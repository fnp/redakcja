import os
from StringIO import StringIO
import logging
logger = logging.getLogger("fnp.wiki")

from lxml import etree

from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_POST, require_GET
from django.core.urlresolvers import reverse
from wiki.helpers import (JSONResponse, JSONFormInvalid, JSONServerError,
                ajax_require_permission, recursive_groupby, active_tab)
from wiki import helpers
from django import http
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404

from wiki.models import Book, Chunk, Theme
from wiki import forms
from datetime import datetime
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import decorator_from_middleware
from django.middleware.gzip import GZipMiddleware

import librarian.html
import librarian.text
from wiki import xml_tools
from apiclient import api_call

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

import nice_diff
import operator

MAX_LAST_DOCS = 10


@active_tab('all')
@never_cache
def document_list(request):
    chunks_list = helpers.ChunksList(Chunk.objects.order_by(
        'book__title', 'book', 'number'))

    return direct_to_template(request, 'wiki/document_list.html', extra_context={
        'books': chunks_list,
        #'books': [helpers.BookChunks(b) for b in Book.objects.all().select_related()],
        'last_books': sorted(request.session.get("wiki_last_books", {}).items(),
                        key=lambda x: x[1]['time'], reverse=True),
    })


@active_tab('unassigned')
@never_cache
def unassigned(request):
    chunks_list = helpers.ChunksList(Chunk.objects.filter(
        user=None).order_by('book__title', 'book__id', 'number'))

    return direct_to_template(request, 'wiki/document_list.html', extra_context={
        'books': chunks_list,
        'last_books': sorted(request.session.get("wiki_last_books", {}).items(),
                        key=lambda x: x[1]['time'], reverse=True),
    })


@never_cache
def user(request, username=None):
    if username is None:
        if request.user.is_authenticated():
            user = request.user
        else:
            raise Http404
    else:
        user = get_object_or_404(User, username=username)

    chunks_list = helpers.ChunksList(Chunk.objects.filter(
        user=user).order_by('book__title', 'book', 'number'))

    return direct_to_template(request, 'wiki/document_list.html', extra_context={
        'books': chunks_list,
        'last_books': sorted(request.session.get("wiki_last_books", {}).items(),
                        key=lambda x: x[1]['time'], reverse=True),
    })
my = login_required(active_tab('my')(user))


@active_tab('users')
def users(request):
    return direct_to_template(request, 'wiki/user_list.html', extra_context={
        'users': User.objects.all().annotate(count=Count('chunk')).order_by(
            '-count', 'last_name', 'first_name'),
    })


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
                return http.HttpResponseRedirect(reverse("wiki_create_missing", args=[slug]))
        else:
            raise Http404

    access_time = datetime.now()
    last_books = request.session.get("wiki_last_books", {})
    last_books[slug, chunk.slug] = {
        'time': access_time,
        'title': chunk.pretty_name(),
        }

    if len(last_books) > MAX_LAST_DOCS:
        oldest_key = min(last_books, key=lambda x: last_books[x]['time'])
        del last_books[oldest_key]
    request.session['wiki_last_books'] = last_books

    return direct_to_template(request, template_name, extra_context={
        'chunk': chunk,
        'forms': {
            "text_save": forms.DocumentTextSaveForm(prefix="textsave"),
            "text_revert": forms.DocumentTextRevertForm(prefix="textrevert"),
            "add_tag": forms.DocumentTagForm(prefix="addtag"),
            "pubmark": forms.DocumentPubmarkForm(prefix="pubmark"),
        },
        'REDMINE_URL': settings.REDMINE_URL,
    })


@require_GET
def editor_readonly(request, slug, chunk=None, template_name='wiki/document_details_readonly.html'):
    try:
        chunk = Chunk.get(slug, chunk)
        revision = request.GET['revision']
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist, KeyError):
        raise Http404

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

    return direct_to_template(request, template_name, extra_context={
        'chunk': chunk,
        'revision': revision,
        'readonly': True,
        'REDMINE_URL': settings.REDMINE_URL,
    })


@active_tab('create')
def create_missing(request, slug=None):
    if slug is None:
        slug = ''
    slug = slug.replace(' ', '-')

    if request.method == "POST":
        form = forms.DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            
            if request.user.is_authenticated():
                creator = request.user
            else:
                creator = None
            book = Book.create(creator=creator,
                slug=form.cleaned_data['slug'],
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
            )

            return http.HttpResponseRedirect(reverse("wiki_editor", args=[book.slug]))
    else:
        form = forms.DocumentCreateForm(initial={
                "slug": slug,
                "title": slug.replace('-', ' ').title(),
        })

    return direct_to_template(request, "wiki/document_create_missing.html", extra_context={
        "slug": slug,
        "form": form,
    })


@active_tab('upload')
def upload(request):
    if request.method == "POST":
        form = forms.DocumentsUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import slughifi

            if request.user.is_authenticated():
                creator = request.user
            else:
                creator = None

            zip = form.cleaned_data['zip']
            skipped_list = []
            ok_list = []
            error_list = []
            slugs = {}
            existing = [book.slug for book in Book.objects.all()]
            for filename in zip.namelist():
                if filename[-1] == '/':
                    continue
                title = os.path.basename(filename)[:-4]
                slug = slughifi(title)
                if not (slug and filename.endswith('.xml')):
                    skipped_list.append(filename)
                elif slug in slugs:
                    error_list.append((filename, slug, _('Slug already used for %s' % slugs[slug])))
                elif slug in existing:
                    error_list.append((filename, slug, _('Slug already used in repository.')))
                else:
                    try:
                        zip.read(filename).decode('utf-8') # test read
                        ok_list.append((filename, slug, title))
                    except UnicodeDecodeError:
                        error_list.append((filename, title, _('File should be UTF-8 encoded.')))
                    slugs[slug] = filename

            if not error_list:
                for filename, slug, title in ok_list:
                    Book.create(creator=creator,
                        slug=slug,
                        title=title,
                        text=zip.read(filename).decode('utf-8'),
                    )

            return direct_to_template(request, "wiki/document_upload.html", extra_context={
                "form": form,
                "ok_list": ok_list,
                "skipped_list": skipped_list,
                "error_list": error_list,
            })
    else:
        form = forms.DocumentsUploadForm()

    return direct_to_template(request, "wiki/document_upload.html", extra_context={
        "form": form,
    })


@never_cache
@decorator_from_middleware(GZipMiddleware)
def text(request, slug, chunk=None):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404

    if request.method == 'POST':
        form = forms.DocumentTextSaveForm(request.POST, prefix="textsave")
        if form.is_valid():
            if request.user.is_authenticated():
                author = request.user
            else:
                author = None
            text = form.cleaned_data['text']
            parent_revision = form.cleaned_data['parent_revision']
            parent = doc.at_revision(parent_revision)
            stage = form.cleaned_data['stage_completed']
            tags = [stage] if stage else []
            doc.commit(author=author,
                       text=text,
                       parent=parent,
                       description=form.cleaned_data['comment'],
                       tags=tags,
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
            revision = None

        return JSONResponse({
            'text': doc.at_revision(revision).materialize(),
            'meta': {},
            'revision': revision if revision else doc.revision(),
        })


@never_cache
def book_xml(request, slug):
    xml = get_object_or_404(Book, slug=slug).materialize()

    response = http.HttpResponse(xml, content_type='application/xml', mimetype='application/wl+xml')
    response['Content-Disposition'] = 'attachment; filename=%s.xml' % slug
    return response


@never_cache
def book_txt(request, slug):
    xml = get_object_or_404(Book, slug=slug).materialize()
    output = StringIO()
    # errors?
    librarian.text.transform(StringIO(xml), output)
    text = output.getvalue()
    response = http.HttpResponse(text, content_type='text/plain', mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.txt' % slug
    return response


@never_cache
def book_html(request, slug):
    xml = get_object_or_404(Book, slug=slug).materialize()
    output = StringIO()
    # errors?
    librarian.html.transform(StringIO(xml), output, parse_dublincore=False,
                             flags=['full-page'])
    html = output.getvalue()
    response = http.HttpResponse(html, content_type='text/html', mimetype='text/html')
    return response


@never_cache
@require_POST
def revert(request, slug, chunk=None):
    form = forms.DocumentTextRevertForm(request.POST, prefix="textrevert")
    if form.is_valid():
        try:
            doc = Chunk.get(slug, chunk)
        except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
            raise Http404

        revision = form.cleaned_data['revision']

        comment = form.cleaned_data['comment']
        comment += "\n#revert to %s" % revision

        if request.user.is_authenticated():
            author = request.user
        else:
            author = None

        before = doc.revision()
        logger.info("Reverting %s to %s", slug, revision)
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
    except (IndexError, OSError):
        logger.exception("Unable to fetch gallery")
        raise http.Http404


@never_cache
def diff(request, slug, chunk=None):
    revA = int(request.GET.get('from', 0))
    revB = int(request.GET.get('to', 0))

    if revA > revB:
        revA, revB = revB, revA

    if revB == 0:
        revB = None

    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    docA = doc.at_revision(revA).materialize()
    docB = doc.at_revision(revB).materialize()

    return http.HttpResponse(nice_diff.html_diff_table(docA.splitlines(),
                                         docB.splitlines(), context=3))


@never_cache
def revision(request, slug, chunk=None):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    return http.HttpResponse(str(doc.revision()))


@never_cache
def history(request, slug, chunk=None):
    # TODO: pagination
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404

    changes = []
    for change in doc.history().order_by('-created_at'):
        changes.append({
                "version": change.revision,
                "description": change.description,
                "author": change.author_str(),
                "date": change.created_at,
                "publishable": "Publishable\n" if change.publishable else "",
                "tag": ',\n'.join(unicode(tag) for tag in change.tags.all()),
            })
    return JSONResponse(changes)


def book(request, slug):
    book = get_object_or_404(Book, slug=slug)

    # TODO: most of this should go somewhere else

    # do we need some automation?
    first_master = None
    chunks = []
    need_fixing = False
    choose_master = False

    length = len(book)
    for i, chunk in enumerate(book):
        chunk_dict = {
            "chunk": chunk,
            "fix": [],
            "grade": ""
            }
        graded = xml_tools.GradedText(chunk.materialize())
        if graded.is_wl():
            master = graded.master()
            if first_master is None:
                first_master = master
            elif master != first_master:
                chunk_dict['fix'].append('bad-master')

            if i > 0 and not graded.has_trim_begin():
                chunk_dict['fix'].append('trim-begin')
            if i < length - 1 and not graded.has_trim_end():
                chunk_dict['fix'].append('trim-end')

            if chunk_dict['fix']:
                chunk_dict['grade'] = 'wl-fix'
            else:
                chunk_dict['grade'] = 'wl'

        elif graded.is_broken_wl():
            chunk_dict['grade'] = 'wl-broken'
        elif graded.is_xml():
            chunk_dict['grade'] = 'xml'
        else:
            chunk_dict['grade'] = 'plain'
            chunk_dict['fix'].append('wl')
            choose_master = True

        if chunk_dict['fix']:
            need_fixing = True
        chunks.append(chunk_dict)

    if first_master or not need_fixing:
        choose_master = False

    if request.method == "POST":
        form = forms.ChooseMasterForm(request.POST)
        if not choose_master or form.is_valid():
            if choose_master:
                first_master = form.cleaned_data['master']

            # do the actual fixing
            for c in chunks:
                if not c['fix']:
                    continue

                text = c['chunk'].materialize()
                for fix in c['fix']:
                    if fix == 'bad-master':
                        text = xml_tools.change_master(text, first_master)
                    elif fix == 'trim-begin':
                        text = xml_tools.add_trim_begin(text)
                    elif fix == 'trim-end':
                        text = xml_tools.add_trim_end(text)
                    elif fix == 'wl':
                        text = xml_tools.basic_structure(text, first_master)
                author = request.user if request.user.is_authenticated() else None
                description = "auto-fix: " + ", ".join(c['fix'])
                c['chunk'].commit(text=text, author=author, 
                    description=description)

            return http.HttpResponseRedirect(book.get_absolute_url())
    elif choose_master:
        form = forms.ChooseMasterForm()
    else:
        form = None

    return direct_to_template(request, "wiki/book_detail.html", extra_context={
        "book": book,
        "chunks": chunks,
        "need_fixing": need_fixing,
        "choose_master": choose_master,
        "first_master": first_master,
        "form": form,
    })


def chunk_add(request, slug, chunk):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404

    if request.method == "POST":
        form = forms.ChunkAddForm(request.POST, instance=doc)
        if form.is_valid():
            if request.user.is_authenticated():
                creator = request.user
            else:
                creator = None
            doc.split(creator=creator,
                slug=form.cleaned_data['slug'],
                comment=form.cleaned_data['comment'],
            )

            return http.HttpResponseRedirect(doc.book.get_absolute_url())
    else:
        form = forms.ChunkAddForm(initial={
                "slug": str(doc.number + 1),
                "comment": "cz. %d" % (doc.number + 1, ),
        })

    return direct_to_template(request, "wiki/chunk_add.html", extra_context={
        "chunk": doc,
        "form": form,
    })


def chunk_edit(request, slug, chunk):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    if request.method == "POST":
        form = forms.ChunkForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(doc.book.get_absolute_url())
    else:
        form = forms.ChunkForm(instance=doc)
    return direct_to_template(request, "wiki/chunk_edit.html", extra_context={
        "chunk": doc,
        "form": form,
    })


def book_append(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.method == "POST":
        form = forms.BookAppendForm(request.POST)
        if form.is_valid():
            append_to = form.cleaned_data['append_to']
            append_to.append(book)
            return http.HttpResponseRedirect(append_to.get_absolute_url())
    else:
        form = forms.BookAppendForm()
    return direct_to_template(request, "wiki/book_append_to.html", extra_context={
        "book": book,
        "form": form,
    })


def book_edit(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.method == "POST":
        form = forms.BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(book.get_absolute_url())
    else:
        form = forms.BookForm(instance=book)
    return direct_to_template(request, "wiki/book_edit.html", extra_context={
        "book": book,
        "form": form,
    })


@require_POST
@ajax_require_permission('wiki.can_change_tags')
def add_tag(request, slug, chunk=None):
    form = forms.DocumentTagForm(request.POST, prefix="addtag")
    if form.is_valid():
        try:
            doc = Chunk.get(slug, chunk)
        except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
            raise Http404

        tag = form.cleaned_data['tag']
        revision = form.cleaned_data['revision']
        doc.at_revision(revision).tags.add(tag)
        return JSONResponse({"message": _("Tag added")})
    else:
        return JSONFormInvalid(form)


@require_POST
@ajax_require_permission('wiki.can_pubmark')
def pubmark(request, slug, chunk=None):
    form = forms.DocumentPubmarkForm(request.POST, prefix="pubmark")
    if form.is_valid():
        try:
            doc = Chunk.get(slug, chunk)
        except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
            raise Http404

        revision = form.cleaned_data['revision']
        publishable = form.cleaned_data['publishable']
        change = doc.at_revision(revision)
        print publishable, change.publishable
        if publishable != change.publishable:
            change.publishable = publishable
            change.save()
            return JSONResponse({"message": _("Revision marked")})
        else:
            return JSONResponse({"message": _("Nothing changed")})
    else:
        return JSONFormInvalid(form)


@require_POST
@login_required
def publish(request, slug):
    book = get_object_or_404(Book, slug=slug)
    try:
        ret = api_call(request.user, "books", {"book_xml": book.materialize()})
    except BaseException, e:
        return http.HttpResponse(e)
    else:
        book.last_published = datetime.now()
        book.save()
        return http.HttpResponseRedirect(book.get_absolute_url())


def themes(request):
    prefix = request.GET.get('q', '')
    return http.HttpResponse('\n'.join([str(t) for t in Theme.objects.filter(name__istartswith=prefix)]))
