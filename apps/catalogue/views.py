from datetime import datetime
import logging
import os
from StringIO import StringIO
from urllib import unquote
from urlparse import urlsplit, urlunsplit

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django import http
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template

import librarian.html
import librarian.text

from apiclient import NotAuthorizedError
from catalogue import forms
from catalogue import helpers
from catalogue.helpers import active_tab
from catalogue.models import Book, Chunk, BookPublishRecord, ChunkPublishRecord
from catalogue.tasks import publishable_error
from catalogue import xml_tools

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

logger = logging.getLogger("fnp.catalogue")


@active_tab('all')
@never_cache
def document_list(request):
    return render(request, 'catalogue/document_list.html')


@never_cache
def user(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'catalogue/user_page.html', {"viewed_user": user})


@login_required
@active_tab('my')
@never_cache
def my(request):
    return render(request, 'catalogue/my_page.html', {
        'last_books': sorted(request.session.get("wiki_last_books", {}).items(),
                        key=lambda x: x[1]['time'], reverse=True),

        "logout_to": '/',
        })


@active_tab('users')
def users(request):
    return direct_to_template(request, 'catalogue/user_list.html', extra_context={
        'users': User.objects.all().annotate(count=Count('chunk')).order_by(
            '-count', 'last_name', 'first_name'),
    })


@active_tab('activity')
def activity(request):
    return render(request, 'catalogue/activity.html')


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return http.HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))


@permission_required('catalogue.add_book')
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
            book = Book.create(
                text=form.cleaned_data['text'],
                creator=creator,
                slug=form.cleaned_data['slug'],
                title=form.cleaned_data['title'],
            )

            return http.HttpResponseRedirect(reverse("wiki_editor", args=[book.slug]))
    else:
        form = forms.DocumentCreateForm(initial={
                "slug": slug,
                "title": slug.replace('-', ' ').title(),
        })

    return direct_to_template(request, "catalogue/document_create_missing.html", extra_context={
        "slug": slug,
        "form": form,

        "logout_to": '/',
    })


@permission_required('catalogue.add_book')
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
                    book = Book.create(
                        text=zip.read(filename).decode('utf-8'),
                        creator=creator,
                        slug=slug,
                        title=title,
                    )

            return direct_to_template(request, "catalogue/document_upload.html", extra_context={
                "form": form,
                "ok_list": ok_list,
                "skipped_list": skipped_list,
                "error_list": error_list,

                "logout_to": '/',
            })
    else:
        form = forms.DocumentsUploadForm()

    return direct_to_template(request, "catalogue/document_upload.html", extra_context={
        "form": form,

        "logout_to": '/',
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
def revision(request, slug, chunk=None):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    return http.HttpResponse(str(doc.revision()))


def book(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if request.user.has_perm('catalogue.change_book'):
        if request.method == "POST":
            form = forms.BookForm(request.POST, instance=book)
            if form.is_valid():
                form.save()
                return http.HttpResponseRedirect(book.get_absolute_url())
        else:
            form = forms.BookForm(instance=book)
            editable = True
    else:
        form = forms.ReadonlyBookForm(instance=book)
        editable = False

    task = publishable_error.delay(book)
    publish_error = task.wait()
    publishable = publish_error is None

    return direct_to_template(request, "catalogue/book_detail.html", extra_context={
        "book": book,
        "publishable": publishable,
        "publishable_error": publish_error,
        "form": form,
        "editable": editable,
    })


@permission_required('catalogue.add_chunk')
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
                title=form.cleaned_data['title'],
            )

            return http.HttpResponseRedirect(doc.book.get_absolute_url())
    else:
        form = forms.ChunkAddForm(initial={
                "slug": str(doc.number + 1),
                "title": "cz. %d" % (doc.number + 1, ),
        })

    return direct_to_template(request, "catalogue/chunk_add.html", extra_context={
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
            go_next = request.GET.get('next', None)
            if go_next:
                go_next = urlquote_plus(unquote(iri_to_uri(go_next)), safe='/?=&')
            else:
                go_next = doc.book.get_absolute_url()
            return http.HttpResponseRedirect(go_next)
    else:
        form = forms.ChunkForm(instance=doc)

    parts = urlsplit(request.META['HTTP_REFERER'])
    parts = ['', ''] + list(parts[2:])
    go_next = urlquote_plus(urlunsplit(parts))

    return direct_to_template(request, "catalogue/chunk_edit.html", extra_context={
        "chunk": doc,
        "form": form,
        "go_next": go_next,
    })


@permission_required('catalogue.change_book')
def book_append(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.method == "POST":
        form = forms.BookAppendForm(book, request.POST)
        if form.is_valid():
            append_to = form.cleaned_data['append_to']
            append_to.append(book)
            return http.HttpResponseRedirect(append_to.get_absolute_url())
    else:
        form = forms.BookAppendForm(book)
    return direct_to_template(request, "catalogue/book_append_to.html", extra_context={
        "book": book,
        "form": form,

        "logout_to": '/',
    })


@require_POST
@login_required
def publish(request, slug):
    book = get_object_or_404(Book, slug=slug)
    try:
        book.publish(request.user)
    except NotAuthorizedError:
        return http.HttpResponseRedirect(reverse('apiclient_oauth'))
    except BaseException, e:
        return http.HttpResponse(e)
    else:
        return http.HttpResponseRedirect(book.get_absolute_url())
