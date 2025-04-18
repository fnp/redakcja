# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, date, timedelta
from itertools import zip_longest
import json
import logging
import os
from urllib.parse import quote_plus, unquote, urlsplit, urlunsplit

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.db.models import Count, Q
from django.db import transaction
from django import http
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import iri_to_uri
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django_cas_ng.decorators import user_passes_test
import requests
from lxml import etree

from librarian import epubcheck
from librarian.html import raw_printable_text

from apiclient import api_call, NotAuthorizedError
from . import forms
from . import helpers
from .helpers import active_tab
from .models import (Book, Chunk, Image, BookPublishRecord, 
        ChunkPublishRecord, ImagePublishRecord, Project)
import catalogue.models
from fileupload.views import UploadView

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

logger = logging.getLogger("fnp.documents")


@active_tab('all')
@never_cache
def document_list(request):
    return render(request, 'documents/document_list.html')


@active_tab('images')
@never_cache
def image_list(request, user=None):
    return render(request, 'documents/image_list.html')


@never_cache
def user(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'documents/user_page.html', {"viewed_user": user})


@login_required
@active_tab('my')
@never_cache
def my(request):
    last_books = sorted(request.session.get("wiki_last_books", {}).items(),
        key=lambda x: x[1]['time'], reverse=True)
    for k, v in last_books:
        v['time'] = datetime.fromtimestamp(v['time'])
    try:
        resp = api_call(request.user, 'username/')
    except NotAuthorizedError:
        wllogin = None
    else:
        wllogin = resp['username']

    return render(request, 'documents/my_page.html', {
        'last_books': last_books,
        "logout_to": '/',
        "wllogin": wllogin,
        })


@active_tab('users')
def users(request):
    return render(request, 'documents/user_list.html', {
        'users': User.objects.all().annotate(count=Count('chunk')).order_by(
            '-count', 'last_name', 'first_name'),
    })


@active_tab('activity')
def activity(request, isodate=None):
    today = date.today()
    try:
        day = helpers.parse_isodate(isodate)
    except ValueError:
        day = today

    if day > today:
        raise Http404
    if day != today:
        next_day = day + timedelta(1)
    prev_day = day - timedelta(1)

    return render(request, 'documents/activity.html', locals())


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return http.HttpResponseRedirect(quote_plus(request.GET.get('next', '/'), safe='/?='))


@permission_required('documents.add_book')
@active_tab('create')
def create_missing(request, slug=None):
    if slug is None:
        slug = ''
    slug = slug.replace(' ', '-')

    if request.method == "POST":
        form = forms.DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            
            if request.user.is_authenticated:
                creator = request.user
            else:
                creator = None
            book = Book.create(
                text=form.cleaned_data['text'],
                creator=creator,
                slug=form.cleaned_data['slug'],
                title=form.cleaned_data['title'],
                gallery=form.cleaned_data['gallery'],
            )

            return http.HttpResponseRedirect(reverse("documents_book", args=[book.slug]))
    else:
        form = forms.DocumentCreateForm(initial={
                "slug": slug,
                "title": slug.replace('-', ' ').title(),
                "gallery": slug,
        })

    return render(request, "documents/document_create_missing.html", {
        "slug": slug,
        "form": form,

        "logout_to": '/',
    })


@permission_required('documents.add_book')
@active_tab('upload')
def upload(request):
    if request.method == "POST":
        form = forms.DocumentsUploadForm(request.POST, request.FILES)
        if form.is_valid():
            from slugify import slugify

            if request.user.is_authenticated:
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
                slug = slugify(title)
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

            return render(request, "documents/document_upload.html", {
                "form": form,
                "ok_list": ok_list,
                "skipped_list": skipped_list,
                "error_list": error_list,

                "logout_to": '/',
            })
    else:
        form = forms.DocumentsUploadForm()

    return render(request, "documents/document_upload.html", {
        "form": form,

        "logout_to": '/',
    })


def serve_xml(request, book, slug):
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")
    xml = book.materialize(publishable=True)
    response = http.HttpResponse(xml, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=%s.xml' % slug
    return response


@never_cache
def book_xml(request, slug):
    book = get_object_or_404(Book, slug=slug)
    return serve_xml(request, book, slug)


@never_cache
def book_xml_dc(request, slug):
    book = get_object_or_404(Book, dc_slug=slug)
    return serve_xml(request, book, slug)


@never_cache
def book_txt(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    doc = book.wldocument()
    text = doc.as_text().get_bytes()
    response = http.HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.txt' % slug
    return response


@never_cache
def book_html(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    doc = book.wldocument(parse_dublincore=False)
    html = doc.as_html(options={'gallery': "'%s'" % book.gallery_url()})

    html = html.get_bytes().decode('utf-8') if html is not None else ''
    # response = http.HttpResponse(html, content_type='text/html')
    # return response
    # book_themes = {}
    # for fragment in book.fragments.all().iterator():
    #     for theme in fragment.tags.filter(category='theme').iterator():
    #         book_themes.setdefault(theme, []).append(fragment)

    # book_themes = book_themes.items()
    # book_themes.sort(key=lambda s: s[0].sort_key)
    return render(request, 'documents/book_text.html', locals())


@login_required
@never_cache
def book_pdf(request, slug, mobile=False):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # TODO: move to celery
    doc = book.wldocument()
    # TODO: error handling
    customizations = ['26pt', 'nothemes', 'nomargins', 'notoc'] if mobile else None
    pdf_file = doc.as_pdf(cover=True, base_url=request.build_absolute_uri(book.gallery_path()), customizations=customizations)
    from .ebook_utils import serve_file
    return serve_file(pdf_file.get_filename(),
                book.slug + '.pdf', 'application/pdf')


@login_required
@never_cache
def book_epub(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # TODO: move to celery
    doc = book.wldocument(librarian2=True)
    # TODO: error handling

    from librarian.builders import EpubBuilder
    epub = EpubBuilder(
        base_url='file://' + book.gallery_path() + '/',
        debug=True
    ).build(doc).get_bytes()
    response = HttpResponse(content_type='application/epub+zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % book.slug + '.epub'
    response.write(epub)
    return response


@login_required
@never_cache
def book_epubcheck(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # TODO: move to celery
    doc = book.wldocument(librarian2=True)
    # TODO: error handling

    from librarian.builders import EpubBuilder
    epub = EpubBuilder(
        base_url='file://' + book.gallery_path() + '/',
        debug=True
    ).build(doc)
    fname = epub.get_filename()

    messages = epubcheck.epubcheck(fname)
    for message in messages:
        for location in message.get('locations', []):
            if 'wl_chunk' in location:
                location['wl_chunk'] = book[location['wl_chunk']]
    return render(request, 'documents/book_epubcheck.html', {
        'messages': messages,
        'book': book,
    })


@login_required
@never_cache
def book_mobi(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # TODO: move to celery
    doc = book.wldocument(librarian2=True)
    # TODO: error handling
    from librarian.builders import MobiBuilder
    mobi = MobiBuilder(
        base_url='file://' + book.gallery_path() + '/'
    ).build(doc).get_bytes()
    response = HttpResponse(content_type='application/x-mobipocket-ebook')
    response['Content-Disposition'] = 'attachment; filename=%s' % book.slug + '.mobi'
    response.write(mobi)
    return response


@never_cache
def revision(request, slug, chunk=None):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")
    return http.HttpResponse(str(doc.revision()))


def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.user.has_perm('documents.change_book'):
        if request.method == "POST":
            form = forms.BookForm(request.POST, instance=book)
            if form.is_valid():
                form.save()
                return http.HttpResponseRedirect(book.get_absolute_url())
        else:
            form = forms.BookForm(instance=book)
        publish_options_form = forms.PublishOptionsForm()
        editable = True
    else:
        form = forms.ReadonlyBookForm(instance=book)
        publish_options_form = forms.PublishOptionsForm()
        editable = False

    publish_error = book.publishable_error()
    publishable = publish_error is None

    stats = None
    try:
        doc = book.wldocument(librarian2=True)
    except:
        doc = None
    else:
        try:
            stats = doc.get_statistics()
        except:
            pass

    cbook_by_slug = None
    if book.dc_slug:
        audio_items = requests.get(f'https://audio.wolnelektury.pl/archive/book/{book.dc_slug}.json').json()['items']
        has_audio = bool(audio_items)
        can_sell_audio = has_audio and all(x['project']['can_sell'] for x in audio_items)

        if book.catalogue_book is None or book.dc_slug != book.catalogue_book.slug:
            cbook_by_slug = catalogue.models.Book.objects.filter(slug=book.dc_slug).first()
    else:
        has_audio = None
        can_sell_audio = None

    return render(request, "documents/book_detail.html", {
        "book": book,
        "doc": doc,
        "stats": stats,
        "publishable": publishable,
        "publishable_error": publish_error,
        "form": form,
        "publish_options_form": publish_options_form,
        "editable": editable,
        "has_audio": has_audio,
        "can_sell_audio": can_sell_audio,
        "cbook_by_slug": cbook_by_slug,
    })


def image(request, slug):
    image = get_object_or_404(Image, slug=slug)
    if not image.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.user.has_perm('documents.change_image'):
        if request.method == "POST":
            form = forms.ImageForm(request.POST, instance=image)
            if form.is_valid():
                form.save()
                return http.HttpResponseRedirect(image.get_absolute_url())
        else:
            form = forms.ImageForm(instance=image)
        editable = True
    else:
        form = forms.ReadonlyImageForm(instance=image)
        editable = False

    publish_error = image.publishable_error()
    publishable = publish_error is None

    return render(request, "documents/image_detail.html", {
        "object": image,
        "publishable": publishable,
        "publishable_error": publish_error,
        "form": form,
        "editable": editable,
    })


@permission_required('documents.add_chunk')
def chunk_add(request, slug, chunk):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.method == "POST":
        form = forms.ChunkAddForm(request.POST, instance=doc)
        if form.is_valid():
            if request.user.is_authenticated:
                creator = request.user
            else:
                creator = None
            doc.split(creator=creator,
                slug=form.cleaned_data['slug'],
                title=form.cleaned_data['title'],
                gallery_start=form.cleaned_data['gallery_start'],
                user=form.cleaned_data['user'],
                stage=form.cleaned_data['stage']
            )

            return http.HttpResponseRedirect(doc.book.get_absolute_url())
    else:
        form = forms.ChunkAddForm(initial={
                "slug": str(doc.number + 1),
                "title": "cz. %d" % (doc.number + 1, ),
        })

    return render(request, "documents/chunk_add.html", {
        "chunk": doc,
        "form": form,
    })


@login_required
def chunk_edit(request, slug, chunk):
    try:
        doc = Chunk.get(slug, chunk)
    except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
        raise Http404
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.method == "POST":
        form = forms.ChunkForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            go_next = request.GET.get('next', None)
            if go_next:
                go_next = quote_plus(unquote(iri_to_uri(go_next)), safe='/?=&')
            else:
                go_next = doc.book.get_absolute_url()
            return http.HttpResponseRedirect(go_next)
    else:
        form = forms.ChunkForm(instance=doc)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        parts = urlsplit(referer)
        parts = ['', ''] + list(parts[2:])
        go_next = quote_plus(urlunsplit(parts))
    else:
        go_next = ''

    return render(request, "documents/chunk_edit.html", {
        "chunk": doc,
        "form": form,
        "go_next": go_next,
    })


@transaction.atomic
@login_required
@require_POST
def chunk_mass_edit(request):
    ids = [int(i) for i in request.POST.get('ids').split(',') if i.strip()]
    chunks = list(Chunk.objects.filter(id__in=ids))
    
    stage = request.POST.get('stage')
    if stage:
        try:
            stage = Chunk.tag_model.objects.get(slug=stage)
        except Chunk.DoesNotExist as e:
            stage = None
       
        for c in chunks: c.stage = stage

    username = request.POST.get('user')
    logger.info("username: %s" % username)
    logger.info(request.POST)
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            user = None
            
        for c in chunks: c.user = user

    project_id = request.POST.get('project')
    if project_id:
        try:
            project = Project.objects.get(pk=int(project_id))
        except (Project.DoesNotExist, ValueError) as e:
            project = None
        for c in chunks:
            book = c.book
            book.project = project
            book.save()

    for c in chunks: c.save()

    return HttpResponse("", content_type="text/plain")


@transaction.atomic
@login_required
@require_POST
def image_mass_edit(request):
    ids = map(int, filter(lambda i: i.strip()!='', request.POST.get('ids').split(',')))
    images = map(lambda i: Image.objects.get(id=i), ids)
    
    stage = request.POST.get('stage')
    if stage:
        try:
            stage = Image.tag_model.objects.get(slug=stage)
        except Image.DoesNotExist as e:
            stage = None
       
        for c in images: c.stage = stage

    username = request.POST.get('user')
    logger.info("username: %s" % username)
    logger.info(request.POST)
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            user = None
            
        for c in images: c.user = user

    project_id = request.POST.get('project')
    if project_id:
        try:
            project = Project.objects.get(pk=int(project_id))
        except (Project.DoesNotExist, ValueError) as e:
            project = None
        for c in images:
            c.project = project

    for c in images: c.save()

    return HttpResponse("", content_type="text/plain")


@permission_required('documents.change_book')
def book_append(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.method == "POST":
        form = forms.BookAppendForm(book, request.POST)
        if form.is_valid():
            append_to = form.cleaned_data['append_to']
            append_to.append(book)
            return http.HttpResponseRedirect(append_to.get_absolute_url())
    else:
        form = forms.BookAppendForm(book)
    return render(request, "documents/book_append_to.html", {
        "book": book,
        "form": form,

        "logout_to": '/',
    })


@require_POST
@login_required
def publish(request, slug):
    form = forms.PublishOptionsForm(request.POST)
    if form.is_valid():
        days = form.cleaned_data['days']
        beta = form.cleaned_data['beta']
        hidden = form.cleaned_data['hidden']
    else:
        days = 0
        beta = False
        hidden = False
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    try:
        protocol = 'https://' if request.is_secure() else 'http://'
        book.publish(request.user, host=protocol + request.get_host(), days=days, beta=beta, hidden=hidden)
    except NotAuthorizedError:
        return http.HttpResponseRedirect(reverse('apiclient_oauth' if not beta else 'apiclient_beta_oauth'))
    except BaseException as e:
        return http.HttpResponse(repr(e))
    else:
        return http.HttpResponseRedirect(book.get_absolute_url())


@require_POST
@login_required
def publish_image(request, slug):
    image = get_object_or_404(Image, slug=slug)
    if not image.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    try:
        image.publish(request.user)
    except NotAuthorizedError:
        return http.HttpResponseRedirect(reverse('apiclient_oauth'))
    except BaseException as e:
        return http.HttpResponse(e)
    else:
        return http.HttpResponseRedirect(image.get_absolute_url())


class GalleryView(UploadView):
    def get_object(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        if not book.gallery:
            raise Http404
        return book

    def breadcrumbs(self):
        return [
            (_('books'), reverse('documents_document_list')),
            (self.object.title, self.object.get_absolute_url()),
            (_('scan gallery'),),
        ]

    def get_directory(self):
        return "%s%s/" % (settings.IMAGE_DIR, self.object.gallery)


def active_users_list(request, csv=False):
    year = int(request.GET.get('y', date.today().year))
    by_user = defaultdict(lambda: 0)
    by_email = defaultdict(lambda: 0)
    names_by_email = defaultdict(set)
    for change_model in (Chunk.change_model, Image.change_model):
        for c in change_model.objects.filter(
                created_at__year=year).order_by(
                'author', 'author_email', 'author_name').values(
                'author', 'author_name', 'author_email').annotate(
                c=Count('author'), ce=Count('author_email')).distinct():
            if c['author']:
                by_user[c['author']] += c['c']
            else:
                by_email[c['author_email']] += c['ce']
                if (c['author_name'] or '').strip():
                    names_by_email[c['author_email']].add(c['author_name'])
    for user in User.objects.filter(pk__in=by_user):
        by_email[user.email] += by_user[user.pk]
        names_by_email[user.email].add("%s %s" % (user.first_name, user.last_name))

    active_users = []
    for email, count in by_email.items():
        active_users.append((email, names_by_email[email], count))
    active_users.sort(key=lambda x: -x[2])
    if csv:
        return http.HttpResponse(
            '\n'.join((
                ','.join(
                    (str(x[2]), x[0], ','.join(x[1]))
                )
                for x in active_users
            )),
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=redakcja-{year}.csv',
            }
        )
    else:
        return render(request, 'documents/active_users_list.html', {
            'users': active_users,
            'year': year,
        })


@user_passes_test(lambda u: u.is_superuser)
def mark_final(request):
    if request.method == 'POST':
        form = forms.MarkFinalForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('mark_final_completed'))
    else:
        form = forms.MarkFinalForm()
    return render(request, 'documents/mark_final.html', {'form': form})


def mark_final_completed(request):
    return render(request, 'documents/mark_final_completed.html')


@login_required
def synchro(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    if request.method == 'POST':
        #hints = json.loads(request.POST.get('hints'))
        chunk = book[0]
        tree = etree.fromstring(chunk.head.materialize())
        m = tree.find('.//meta[@id="synchro"]')
        if m is None:
            rdf = tree.find('.//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
            m = etree.SubElement(rdf, 'meta', id="synchro")
            m.tail = '\n'
        m.text = request.POST.get('hints')
        text = etree.tostring(tree, encoding='unicode')
        chunk.commit(text, author=request.user, description='Synchronizacja')
        return HttpResponseRedirect('')
    
    document = book.wldocument(librarian2=True, publishable=False)

    slug = document.meta.url.slug
    error = None
    try:
        items = requests.get(f'https://audio.wolnelektury.pl/archive/book/{slug}.json').json()['items']
    except:
        error = 'Błąd połączenia z repozytorium audio.'
        items = []
    else:
        mp3 = [
            item['part'] for item in items
        ]

    split_on = (
        'naglowek_rozdzial',
        'naglowek_scena',
    )
    split_other = (
        'naglowek_czesc',
        'naglowek_akt',
        'naglowek_podrozdzial',
        'srodtytul',
    )

    headers = []
    headers_other = []
    master = document.tree.getroot()[-1]
    for item in master:
        if item.tag in split_on:
            headers.append([
                item.tag,
                raw_printable_text(item),
                0,
                item.sourceline,
            ])
        if item.tag in split_other:
            headers_other.append([
                item.tag,
                raw_printable_text(item),
                0,
                item.sourceline,
            ])

    hints = []
    m = document.tree.find('.//meta[@id="synchro"]')
    if m is not None:
        try:
            hints = json.loads(m.text)
        except:
            raise
            pass
    
    return render(request, 'documents/synchro.html', {
        'book': book,
        'headers': headers,
        'headers_other': headers_other,
        'mp3': mp3,
        'error': error,
        'hints': hints,
    })


@permission_required('documents.change_book')
def attach_book_to_catalogue(request, pk):
    dbook = get_object_or_404(Book, pk=pk)
    if dbook.dc_slug:
        cbook = get_object_or_404(catalogue.models.Book, slug=dbook.dc_slug)
        dbook.catalogue_book = cbook
        dbook.save()
    return http.HttpResponseRedirect(dbook.get_absolute_url())
