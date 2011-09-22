from datetime import datetime
import logging
import os
from StringIO import StringIO

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count
from django import http
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template

import librarian.html
import librarian.text

from catalogue import forms
from catalogue import helpers
from catalogue.helpers import active_tab
from catalogue.models import Book, Chunk, BookPublishRecord, ChunkPublishRecord
from catalogue import xml_tools

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

logger = logging.getLogger("fnp.catalogue")


def foreign_filter(qs, value, filter_field, model, model_field='slug', unset='-'):
    if value == unset:
        return qs.filter(**{filter_field: None})
    if not value:
        return qs
    try:
        obj = model._default_manager.get(**{model_field: value})
    except model.DoesNotExist:
        return qs.none()
    else:
        return qs.filter(**{filter_field: obj})


def search_filter(qs, value, filter_field):
    if not value:
        return qs
    return qs.filter(**{"%s__icontains" % filter_field: value})


@active_tab('all')
@never_cache
def document_list(request, filters=None):
    chunks = Chunk.objects.order_by('book__title', 'book', 'number')

    chunks = foreign_filter(chunks, request.GET.get('user', None), 'user', User, 'username')
    chunks = foreign_filter(chunks, request.GET.get('stage', None), 'stage', Chunk.tag_model, 'slug')
    chunks = search_filter(chunks, request.GET.get('title', None), 'book__title')

    chunks_list = helpers.ChunksList(chunks)

    users = User.objects.annotate(count=Count('chunk')).filter(count__gt=0).order_by('-count', 'last_name', 'first_name')
    #users = User.objects.annotate(count=Count('chunk')).order_by('-count', 'last_name', 'first_name')


    return direct_to_template(request, 'catalogue/document_list.html', extra_context={
        'books': chunks_list,
        'last_books': sorted(request.session.get("wiki_last_books", {}).items(),
                        key=lambda x: x[1]['time'], reverse=True),
        'stages': Chunk.tag_model.objects.all(),
        'users': users,
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

    return direct_to_template(request, 'catalogue/document_list.html', extra_context={
        'books': chunks_list,
        'last_books': sorted(request.session.get("wiki_last_books", {}).items(),
                        key=lambda x: x[1]['time'], reverse=True),
        'viewed_user': user,
        'stages': Chunk.tag_model.objects.all(),
    })
my = login_required(active_tab('my')(user))


@active_tab('users')
def users(request):
    return direct_to_template(request, 'catalogue/user_list.html', extra_context={
        'users': User.objects.all().annotate(count=Count('chunk')).order_by(
            '-count', 'last_name', 'first_name'),
    })


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return http.HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))


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

    return direct_to_template(request, "catalogue/document_create_missing.html", extra_context={
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

            return direct_to_template(request, "catalogue/document_upload.html", extra_context={
                "form": form,
                "ok_list": ok_list,
                "skipped_list": skipped_list,
                "error_list": error_list,
            })
    else:
        form = forms.DocumentsUploadForm()

    return direct_to_template(request, "catalogue/document_upload.html", extra_context={
        "form": form,
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

    # TODO: most of this should go somewhere else

    # do we need some automation?
    first_master = None
    chunks = []
    need_fixing = False
    choose_master = False

    length = book.chunk_set.count()
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

    return direct_to_template(request, "catalogue/book_detail.html", extra_context={
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
            return http.HttpResponseRedirect(doc.book.get_absolute_url())
    else:
        form = forms.ChunkForm(instance=doc)
    return direct_to_template(request, "catalogue/chunk_edit.html", extra_context={
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
    return direct_to_template(request, "catalogue/book_append_to.html", extra_context={
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
    return direct_to_template(request, "catalogue/book_edit.html", extra_context={
        "book": book,
        "form": form,
    })


@require_POST
@login_required
def publish(request, slug):
    book = get_object_or_404(Book, slug=slug)
    try:
        book.publish(request.user)
    except BaseException, e:
        return http.HttpResponse(e)
    else:
        return http.HttpResponseRedirect(book.get_absolute_url())
