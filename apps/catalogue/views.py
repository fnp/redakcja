from datetime import datetime, date, timedelta
import logging
import os
from StringIO import StringIO
from urllib import unquote
from urlparse import urlsplit, urlunsplit

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.db import transaction
from django import http
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, render_to_response
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.template import RequestContext

from apiclient import NotAuthorizedError
from catalogue import forms
from catalogue import helpers
from catalogue.helpers import active_tab
from catalogue.models import Book, Chunk, BookPublishRecord, ChunkPublishRecord
from fileupload.views import UploadView

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
    return render(request, 'catalogue/user_list.html', {
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

    return render(request, 'catalogue/activity.html', locals())


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
                gallery=form.cleaned_data['gallery'],
            )

            return http.HttpResponseRedirect(reverse("catalogue_book", args=[book.slug]))
    else:
        form = forms.DocumentCreateForm(initial={
                "slug": slug,
                "title": slug.replace('-', ' ').title(),
                "gallery": slug,
        })

    return render(request, "catalogue/document_create_missing.html", {
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

            return render(request, "catalogue/document_upload.html", {
                "form": form,
                "ok_list": ok_list,
                "skipped_list": skipped_list,
                "error_list": error_list,

                "logout_to": '/',
            })
    else:
        form = forms.DocumentsUploadForm()

    return render(request, "catalogue/document_upload.html", {
        "form": form,

        "logout_to": '/',
    })


@never_cache
def book_xml(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")
    xml = book.materialize()

    response = http.HttpResponse(xml, content_type='application/xml', mimetype='application/wl+xml')
    response['Content-Disposition'] = 'attachment; filename=%s.xml' % slug
    return response


@never_cache
def book_txt(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    doc = book.wldocument()
    text = doc.as_text().get_string()
    response = http.HttpResponse(text, content_type='text/plain', mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.txt' % slug
    return response


@never_cache
def book_html(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    doc = book.wldocument(parse_dublincore=False)
    html = doc.as_html()

    html = html.get_string() if html is not None else ''
    # response = http.HttpResponse(html, content_type='text/html', mimetype='text/html')
    # return response
    # book_themes = {}
    # for fragment in book.fragments.all().iterator():
    #     for theme in fragment.tags.filter(category='theme').iterator():
    #         book_themes.setdefault(theme, []).append(fragment)

    # book_themes = book_themes.items()
    # book_themes.sort(key=lambda s: s[0].sort_key)
    return render_to_response('catalogue/book_text.html', locals(),
        context_instance=RequestContext(request))


@never_cache
def book_pdf(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # TODO: move to celery
    doc = book.wldocument()
    # TODO: error handling
    pdf_file = doc.as_pdf()
    from catalogue.ebook_utils import serve_file
    return serve_file(pdf_file.get_filename(),
                book.slug + '.pdf', 'application/pdf')


@never_cache
def book_epub(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    # TODO: move to celery
    doc = book.wldocument()
    # TODO: error handling
    epub = doc.as_epub().get_string()
    response = HttpResponse(mimetype='application/epub+zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % book.slug + '.epub'
    response.write(epub)
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

    publish_error = book.publishable_error()
    publishable = publish_error is None

    return render(request, "catalogue/book_detail.html", {
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
    if not doc.book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

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

    return render(request, "catalogue/chunk_add.html", {
        "chunk": doc,
        "form": form,
    })


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
                go_next = urlquote_plus(unquote(iri_to_uri(go_next)), safe='/?=&')
            else:
                go_next = doc.book.get_absolute_url()
            return http.HttpResponseRedirect(go_next)
    else:
        form = forms.ChunkForm(instance=doc)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        parts = urlsplit(referer)
        parts = ['', ''] + list(parts[2:])
        go_next = urlquote_plus(urlunsplit(parts))
    else:
        go_next = ''

    return render(request, "catalogue/chunk_edit.html", {
        "chunk": doc,
        "form": form,
        "go_next": go_next,
    })


@transaction.commit_on_success
def chunk_mass_edit(request):
    if request.method == 'POST':
        ids = map(int, filter(lambda i: i.strip()!='', request.POST.get('ids').split(',')))
        chunks = map(lambda i: Chunk.objects.get(id=i), ids)
        
        stage = request.POST.get('stage')
        if stage:
            try:
                stage = Chunk.tag_model.objects.get(slug=stage)
            except Chunk.DoesNotExist, e:
                stage = None
           
            for c in chunks: c.stage = stage

        username = request.POST.get('user')
        logger.info("username: %s" % username)
        logger.info(request.POST)
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist, e:
                user = None
                
            for c in chunks: c.user = user

        status = request.POST.get('status')
        if status:
            books_affected = set()
            for c in chunks:
                if status == 'publish':
                    c.head.publishable = True
                    c.head.save()
                elif status == 'unpublish':
                    c.head.publishable = False
                    c.head.save()
                c.touch()  # cache
                books_affected.add(c.book)
            for b in books_affected:
                b.touch()  # cache

        for c in chunks: c.save()

        return HttpResponse("", content_type="text/plain")
    else:
        raise Http404


@permission_required('catalogue.change_book')
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
    return render(request, "catalogue/book_append_to.html", {
        "book": book,
        "form": form,

        "logout_to": '/',
    })


@require_POST
@login_required
def publish(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.accessible(request):
        return HttpResponseForbidden("Not authorized.")

    try:
        book.publish(request.user)
    except NotAuthorizedError:
        return http.HttpResponseRedirect(reverse('apiclient_oauth'))
    except BaseException, e:
        return http.HttpResponse(e)
    else:
        return http.HttpResponseRedirect(book.get_absolute_url())


class GalleryView(UploadView):
    def get_object(self, request, slug):
        return get_object_or_404(Book, slug=slug)

    def breadcrumbs(self):
        return [
            (_('books'), reverse('catalogue_document_list')),
            (self.object.title, self.object.get_absolute_url()),
            (_('scan gallery'),),
        ]

    def get_directory(self):
        return "%s%s/" % (settings.IMAGE_DIR, self.object.gallery)
