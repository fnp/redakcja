# -*- coding: utf-8 -*-
from datetime import date, timedelta
import logging
import os
import shutil

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count
from django import http
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.http import urlquote_plus
from django.views.decorators.http import require_POST

from catalogue import forms
from catalogue import helpers
from catalogue.helpers import active_tab
from .constants import STAGES
from .models import Document, Plan
from dvcs.models import Revision
from organizations.models import Organization
from fileupload.views import UploadView, PackageView

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache
# from fnpdjango.utils.text.slughifi import slughifi

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
        'last_books': sorted(
            request.session.get("wiki_last_books", {}).items(), key=lambda x: x[1]['time'], reverse=True),

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


# @permission_required('catalogue.add_book')
@login_required
@active_tab('create')
def create_missing(request):
    if request.method == "POST":
        form = forms.DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            
            if request.user.is_authenticated():
                creator = request.user
            else:
                creator = None

            title = form.cleaned_data['title']
            try:
                org = request.user.membership_set.get(
                    organization=int(form.cleaned_data['owner_organization'])).organization
                kwargs = {'owner_organization': org}
            except:
                kwargs = {'owner_user': request.user}

            doc = Document.objects.create(**kwargs)

            cover = request.FILES.get('cover')
            if cover:
                uppath = 'uploads/%d/' % doc.pk
                path = settings.MEDIA_ROOT + uppath
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest_path = path + cover.name   # UNSAFE
                with open(dest_path, 'w') as destination:
                    for chunk in cover.chunks():
                        destination.write(chunk)
                cover_url = 'http://milpeer.eu/media/dynamic/' + uppath + cover.name
            else:
                cover_url = ''

            doc.commit(
                text='''<section xmlns="http://nowoczesnapolska.org.pl/sst#" xmlns:dc="http://purl.org/dc/elements/1.1/">
                <metadata>
                    <dc:publisher>''' + form.cleaned_data['publisher'] + '''</dc:publisher>
                    <dc:description>''' + form.cleaned_data['description'] + '''</dc:description>
                    <dc:language>''' + form.cleaned_data['language'] + '''</dc:language>
                    <dc:rights>''' + form.cleaned_data['rights'] + '''</dc:rights>
                    <dc:audience>''' + form.cleaned_data['audience'] + '''</dc:audience>
                    <dc:relation.coverImage.url>''' + cover_url + '''</dc:relation.coverImage.url>
                </metadata>
                <header>''' + title + '''</header>
                <div class="p"> </div>
                </section>''',
                author=creator
            )
            doc.assigned_to = request.user
            doc.save()

            return http.HttpResponseRedirect(reverse("wiki_editor", args=[doc.pk]))
    else:
        org_pk = request.GET.get('organization')
        if org_pk:
            try:
                org = Organization.objects.get(pk=org_pk)
            except Organization.DoesNotExist:
                org = None
            else:
                if not org.is_member(request.user):
                    org = None
        else:
            org = None
        if org is not None:
            org = org.pk

        form = forms.DocumentCreateForm(initial={'owner_organization': org})

    return render(request, "catalogue/document_create_missing.html", {
        "form": form,

        "logout_to": '/',
    })


# @permission_required('catalogue.add_book')
# @active_tab('upload')
# def upload(request):
#     if request.method == "POST":
#         form = forms.DocumentsUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             import slughifi
#
#             if request.user.is_authenticated():
#                 creator = request.user
#             else:
#                 creator = None
#
#             zip = form.cleaned_data['zip']
#             skipped_list = []
#             ok_list = []
#             error_list = []
#             slugs = {}
#             existing = [book.slug for book in Book.objects.all()]
#             for filename in zip.namelist():
#                 if filename[-1] == '/':
#                     continue
#                 title = os.path.basename(filename)[:-4]
#                 slug = slughifi(title)
#                 if not (slug and filename.endswith('.xml')):
#                     skipped_list.append(filename)
#                 elif slug in slugs:
#                     error_list.append((filename, slug, _('Slug already used for %s' % slugs[slug])))
#                 elif slug in existing:
#                     error_list.append((filename, slug, _('Slug already used in repository.')))
#                 else:
#                     try:
#                         zip.read(filename).decode('utf-8') # test read
#                         ok_list.append((filename, slug, title))
#                     except UnicodeDecodeError:
#                         error_list.append((filename, title, _('File should be UTF-8 encoded.')))
#                     slugs[slug] = filename
#
#             if not error_list:
#                 for filename, slug, title in ok_list:
#                     book = Book.create(
#                         text=zip.read(filename).decode('utf-8'),
#                         creator=creator,
#                         slug=slug,
#                         title=title,
#                     )
#
#             return render(request, "catalogue/document_upload.html", {
#                 "form": form,
#                 "ok_list": ok_list,
#                 "skipped_list": skipped_list,
#                 "error_list": error_list,
#
#                 "logout_to": '/',
#             })
#     else:
#         form = forms.DocumentsUploadForm()
#
#     return render(request, "catalogue/document_upload.html", {
#         "form": form,
#
#         "logout_to": '/',
#     })


# @never_cache
# def book_xml(request, slug):
#     book = get_object_or_404(Book, slug=slug)
#     if not book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#     xml = book.materialize()
#
#     response = http.HttpResponse(xml, content_type='application/xml', mimetype='application/wl+xml')
#     response['Content-Disposition'] = 'attachment; filename=%s.xml' % slug
#     return response


# @never_cache
# def book_txt(request, slug):
#     book = get_object_or_404(Book, slug=slug)
#     if not book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#
#     doc = book.wldocument()
#     text = doc.as_text().get_string()
#     response = http.HttpResponse(text, content_type='text/plain', mimetype='text/plain')
#     response['Content-Disposition'] = 'attachment; filename=%s.txt' % slug
#     return response


@never_cache
def book_html(request, pk, rev_pk=None, preview=False):
    from librarian.document import Document as SST
    from librarian.formats.html import HtmlFormat

    doc = get_object_or_404(Document, pk=pk, deleted=False)

    try:
        published_revision = doc.publish_log.all()[0].revision
    except IndexError:
        published_revision = None

    if rev_pk is None:
        if preview:
            revision = doc.revision
        else:
            if published_revision is not None:
                revision = published_revision
            else:
                # No published version, fallback to preview mode.
                preview = True
                revision = doc.revision
    else:
        revision = get_object_or_404(Revision, pk=rev_pk)

    was_published = revision == published_revision or doc.publish_log.filter(revision=revision).exists()

    sst = SST.from_string(revision.materialize())
    html = HtmlFormat(sst).build(
        files_path='http://%s/media/dynamic/uploads/%s/' % (request.get_host(), pk)).get_string()

    # response = http.HttpResponse(html, content_type='text/html', mimetype='text/html')
    # return response
    # book_themes = {}
    # for fragment in book.fragments.all().iterator():
    #     for theme in fragment.tags.filter(category='theme').iterator():
    #         book_themes.setdefault(theme, []).append(fragment)

    # book_themes = book_themes.items()
    # book_themes.sort(key=lambda s: s[0].sort_key)
    return render(request, 'catalogue/book_text.html', {
        'doc': doc,
        'preview': preview,
        'revision': revision,
        'published_revision': published_revision,
        'specific': rev_pk is not None,
        'html': html,
        'can_edit': doc.can_edit(request.user) if doc else None,
        'was_published': was_published,
    })


@never_cache
def book_pdf(request, pk, rev_pk):
    from librarian.utils import Context
    from librarian.document import Document as SST
    from librarian.formats.pdf import PdfFormat

    doc = get_object_or_404(Document, pk=pk)
    rev = get_object_or_404(Revision, pk=rev_pk)
    # Test

    sst = SST.from_string(rev.materialize())
    
    ctx = Context(
        files_path='http://%s/media/dynamic/uploads/%s/' % (request.get_host(), pk),
        source_url='http://%s%s' % (request.get_host(), reverse('catalogue_html', args=[doc.pk])),
    )
    if doc.owner_organization is not None and doc.owner_organization.logo:
        ctx.cover_logo = 'http://%s%s' % (request.get_host(), doc.owner_organization.logo.url)
    pdf_file = PdfFormat(sst).build(ctx)

    from catalogue.ebook_utils import serve_file
    return serve_file(pdf_file.get_filename(), '%d.pdf' % doc.pk, 'application/pdf')


@never_cache
def book_epub(request, pk, rev_pk):
    from librarian.utils import Context
    from librarian.document import Document as SST
    from librarian.formats.epub import EpubFormat

    doc = get_object_or_404(Document, pk=pk)
    rev = get_object_or_404(Revision, pk=rev_pk)
    # Test

    sst = SST.from_string(rev.materialize())

    ctx = Context(
        files_path='http://%s/media/dynamic/uploads/%s/' % (request.get_host(), pk),
        source_url='http://%s%s' % (request.get_host(), reverse('catalogue_html', args=[doc.pk])),
    )
    if doc.owner_organization is not None and doc.owner_organization.logo:
        ctx.cover_logo = 'http://%s%s' % (request.get_host(), doc.owner_organization.logo.url)
    epub_file = EpubFormat(sst).build()

    from catalogue.ebook_utils import serve_file
    return serve_file(epub_file.get_filename(), '%d.epub' % doc.pk, 'application/epub+zip')


# @never_cache
# def revision(request, slug, chunk=None):
#     try:
#         doc = Chunk.get(slug, chunk)
#     except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
#         raise Http404
#     if not doc.book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#     return http.HttpResponse(str(doc.revision()))


@login_required
def book_schedule(request, pk):
    book = get_object_or_404(Document, pk=pk, deleted=False)
    if request.method == 'POST':
        Plan.objects.filter(document=book).delete()
        for i, s in enumerate(STAGES):
            user_id = request.POST.get('s%d-user' % i)
            deadline = request.POST.get('s%d-deadline' % i) or None
            Plan.objects.create(document=book, stage=s, user_id=user_id, deadline=deadline)

        book.set_stage(request.POST.get('stage', ''))
        return redirect('catalogue_user')

    current = {}
    for p in Plan.objects.filter(document=book):
        current[p.stage] = (getattr(p.user, 'pk', None), (p.deadline.isoformat() if p.deadline else None))

    schedule = [(i, s, current.get(s, ())) for (i, s) in enumerate(STAGES)]
    
    if book.owner_organization:
        people = [m.user for m in book.owner_organization.membership_set.exclude(status='pending')]
    else:
        people = [book.owner_user]
    return render(request, 'catalogue/book_schedule.html', {
        'book': book,
        'schedule': schedule,
        'people': people,
    })


@login_required
def book_owner(request, pk):
    doc = get_object_or_404(Document, pk=pk, deleted=False)
    user_is_owner = doc.owner_organization and doc.owner_organization.is_member(request.user)
    if not (doc.owner_user == request.user or user_is_owner):
        raise Http404

    error = ''

    if request.method == 'POST':
        # TODO: real form
        new_org_pk = request.POST.get('owner_organization')
        if not new_org_pk:
            doc.owner_organization = None
            doc.owner_user = request.user
            doc.save()
        else:
            org = Organization.objects.get(pk=new_org_pk)
            if not org.is_member(request.user):
                error = 'Bad organization'
            else:
                doc.owner_organization = org
                doc.owner_user = None
                doc.save()
        if not error:
            return redirect('catalogue_user')

    return render(request, 'catalogue/book_owner.html', {
        'doc': doc,
        'error': error,
    })


@login_required
def book_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk, deleted=False)
    if not (doc.owner_user == request.user or doc.owner_organization.is_member(request.user)):
        raise Http404

    if request.method == 'POST':
        doc.deleted = True
        doc.save()
        return redirect('catalogue_user')

    return render(request, 'catalogue/book_delete.html', {
        'doc': doc,
    })


# def book(request, slug):
#     book = get_object_or_404(Book, slug=slug)
#     if not book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#
#     if request.user.has_perm('catalogue.change_book'):
#         if request.method == "POST":
#             form = forms.BookForm(request.POST, instance=book)
#             if form.is_valid():
#                 form.save()
#                 return http.HttpResponseRedirect(book.get_absolute_url())
#         else:
#             form = forms.BookForm(instance=book)
#         editable = True
#     else:
#         form = forms.ReadonlyBookForm(instance=book)
#         editable = False
#
#     publish_error = book.publishable_error()
#     publishable = publish_error is None
#
#     return render(request, "catalogue/book_detail.html", {
#         "book": book,
#         "publishable": publishable,
#         "publishable_error": publish_error,
#         "form": form,
#         "editable": editable,
#     })


# @permission_required('catalogue.add_chunk')
# def chunk_add(request, slug, chunk):
#     try:
#         doc = Chunk.get(slug, chunk)
#     except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
#         raise Http404
#     if not doc.book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#
#     if request.method == "POST":
#         form = forms.ChunkAddForm(request.POST, instance=doc)
#         if form.is_valid():
#             if request.user.is_authenticated():
#                 creator = request.user
#             else:
#                 creator = None
#             doc.split(creator=creator,
#                 slug=form.cleaned_data['slug'],
#                 title=form.cleaned_data['title'],
#                 gallery_start=form.cleaned_data['gallery_start'],
#                 user=form.cleaned_data['user'],
#                 stage=form.cleaned_data['stage']
#             )
#
#             return http.HttpResponseRedirect(doc.book.get_absolute_url())
#     else:
#         form = forms.ChunkAddForm(initial={
#                 "slug": str(doc.number + 1),
#                 "title": "cz. %d" % (doc.number + 1, ),
#         })
#
#     return render(request, "catalogue/chunk_add.html", {
#         "chunk": doc,
#         "form": form,
#     })


# @login_required
# def chunk_edit(request, slug, chunk):
#     try:
#         doc = Chunk.get(slug, chunk)
#     except (Chunk.MultipleObjectsReturned, Chunk.DoesNotExist):
#         raise Http404
#     if not doc.book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#
#     if request.method == "POST":
#         form = forms.ChunkForm(request.POST, instance=doc)
#         if form.is_valid():
#             form.save()
#             go_next = request.GET.get('next', None)
#             if go_next:
#                 go_next = urlquote_plus(unquote(iri_to_uri(go_next)), safe='/?=&')
#             else:
#                 go_next = doc.book.get_absolute_url()
#             return http.HttpResponseRedirect(go_next)
#     else:
#         form = forms.ChunkForm(instance=doc)
#
#     referer = request.META.get('HTTP_REFERER')
#     if referer:
#         parts = urlsplit(referer)
#         parts = ['', ''] + list(parts[2:])
#         go_next = urlquote_plus(urlunsplit(parts))
#     else:
#         go_next = ''
#
#     return render(request, "catalogue/chunk_edit.html", {
#         "chunk": doc,
#         "form": form,
#         "go_next": go_next,
#     })


# @transaction.atomic
# @login_required
# def chunk_mass_edit(request):
#     if request.method == 'POST':
#         ids = map(int, filter(lambda i: i.strip()!='', request.POST.get('ids').split(',')))
#         chunks = map(lambda i: Chunk.objects.get(id=i), ids)
#
#         stage = request.POST.get('stage')
#         if stage:
#             try:
#                 stage = Chunk.tag_model.objects.get(slug=stage)
#             except Chunk.DoesNotExist, e:
#                 stage = None
#
#             for c in chunks: c.stage = stage
#
#         username = request.POST.get('user')
#         logger.info("username: %s" % username)
#         logger.info(request.POST)
#         if username:
#             try:
#                 user = User.objects.get(username=username)
#             except User.DoesNotExist, e:
#                 user = None
#
#             for c in chunks: c.user = user
#
#         status = request.POST.get('status')
#         if status:
#             books_affected = set()
#             for c in chunks:
#                 if status == 'publish':
#                     c.head.publishable = True
#                     c.head.save()
#                 elif status == 'unpublish':
#                     c.head.publishable = False
#                     c.head.save()
#                 c.touch()  # cache
#                 books_affected.add(c.book)
#             for b in books_affected:
#                 b.touch()  # cache
#
#         project_id = request.POST.get('project')
#         if project_id:
#             try:
#                 project = Project.objects.get(pk=int(project_id))
#             except (Project.DoesNotExist, ValueError), e:
#                 project = None
#             for c in chunks:
#                 book = c.book
#                 book.project = project
#                 book.save()
#
#         for c in chunks: c.save()
#
#         return HttpResponse("", content_type="text/plain")
#     else:
#         raise Http404


# @permission_required('catalogue.change_book')
# def book_append(request, slug):
#     book = get_object_or_404(Book, slug=slug)
#     if not book.accessible(request):
#         return HttpResponseForbidden("Not authorized.")
#
#     if request.method == "POST":
#         form = forms.BookAppendForm(book, request.POST)
#         if form.is_valid():
#             append_to = form.cleaned_data['append_to']
#             append_to.append(book)
#             return http.HttpResponseRedirect(append_to.get_absolute_url())
#     else:
#         form = forms.BookAppendForm(book)
#     return render(request, "catalogue/book_append_to.html", {
#         "book": book,
#         "form": form,
#
#         "logout_to": '/',
#     })


@require_POST
@login_required
def publish(request, pk):
    from wiki import forms
    from .models import PublishRecord
    from dvcs.models import Revision

    # FIXME: check permissions

    doc = get_object_or_404(Document, pk=pk, deleted=False)
    form = forms.DocumentTextPublishForm(request.POST, prefix="textpublish")
    if form.is_valid():
        rev = Revision.objects.get(pk=form.cleaned_data['revision'])
        # FIXME: check if in tree
        # if PublishRecord.objects.filter(revision=rev, document=doc).exists():
        #     return http.HttpResponse('exists')
        PublishRecord.objects.create(revision=rev, document=doc, user=request.user)
        if request.is_ajax():
            return http.HttpResponse('ok')
        else:
            return redirect('catalogue_html', doc.pk)
    else:
        if request.is_ajax():
            return http.HttpResponse('error')
        else:
            try:
                return redirect('catalogue_preview_rev', doc.pk, form.cleaned_data['revision'])
            except KeyError:
                return redirect('catalogue_preview', doc.pk)


@require_POST
@login_required
def unpublish(request, pk):
    # FIXME: check permissions

    doc = get_object_or_404(Document, pk=pk, deleted=False)
    doc.publish_log.all().delete()
    if request.is_ajax():
        return http.HttpResponse('ok')
    else:
        return redirect('catalogue_html', doc.pk)


class GalleryMixin(object):
    def get_directory(self):
        # return "%s%s/" % (settings.IMAGE_DIR, 'org%d' % self.org.pk if self.org is not None else self.request.user.pk)
        return "uploads/%d/" % self.doc.pk


class GalleryView(GalleryMixin, UploadView):

    def breadcrumbs(self):
        return [
                (self.doc.meta()['title'], '/documents/%d/' % self.doc.pk),
            ]

    def get_object(self, request, pk=None):
        self.doc = Document.objects.get(pk=pk, deleted=False)


class GalleryPackageView(GalleryMixin, PackageView):

    def get_redirect_url(self, slug):
        return reverse('catalogue_book_gallery', kwargs=dict(slug=slug))


@login_required
def fork(request, pk):
    doc = get_object_or_404(Document, pk=pk, deleted=False)
    if request.method == "POST":
        form = forms.DocumentForkForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                org = request.user.membership_set.get(
                    organization=int(form.cleaned_data['owner_organization'])).organization
                kwargs = {'owner_organization': org}
            except:
                kwargs = {'owner_user': request.user}

            new_doc = Document.objects.create(revision=doc.revision, **kwargs)

            if os.path.isdir(settings.MEDIA_ROOT + "uploads/%d" % doc.pk):
                shutil.copytree(
                    settings.MEDIA_ROOT + "uploads/%d" % doc.pk,
                    settings.MEDIA_ROOT + "uploads/%d" % new_doc.pk
                )

            new_doc.assigned_to = request.user
            new_doc.save()

            return http.HttpResponseRedirect(reverse("wiki_editor", args=[new_doc.pk]))
    else:
        form = forms.DocumentForkForm()

    return render(request, "catalogue/document_fork.html", {
        "form": form,

        "logout_to": '/',
    })


def upcoming(request):
    return render(request, "catalogue/upcoming.html", {
        'objects_list': Document.objects.filter(deleted=False).filter(publish_log=None),
    })


def finished(request):
    return render(request, "catalogue/finished.html", {
        'objects_list': Document.objects.filter(deleted=False).exclude(publish_log=None),
    })
