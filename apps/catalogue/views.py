# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import logging
import os
import shutil
import subprocess
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django import http
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlquote_plus
from django.views.decorators.http import require_POST

from catalogue import forms
from catalogue.forms import TagMultipleForm, TagSingleForm
from catalogue.helpers import active_tab
from catalogue.models import Category
from librarian import BuildError
from redakcja.utlis import send_notify_email
from .constants import STAGES
from .models import Document, Plan
from dvcs.models import Revision
from organizations.models import Organization
from fileupload.views import UploadView

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


@never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return http.HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))


@login_required
@active_tab('create')
def create_missing(request):
    if request.method == "POST":
        form = forms.DocumentCreateForm(request.POST, request.FILES)
        # tag_forms = [
        #     (TagMultipleForm if category.multiple else TagSingleForm)(
        #         category=category, data=request.POST, prefix=category.dc_tag)
        #     for category in Category.objects.all()]
        if form.is_valid():  # and all(tag_form.is_valid() for tag_form in tag_forms):
            
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

        # tag_forms = [
        #     (TagMultipleForm if category.multiple else TagSingleForm)(category=category, prefix=category.dc_tag)
        #     for category in Category.objects.all()]

    return render(request, "catalogue/document_create_missing.html", {
        "form": form,
        # "tag_forms": tag_forms,

        "logout_to": '/',
    })


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

    try:
        sst = SST.from_string(revision.materialize())
    except ValueError as e:
        html = e
    else:
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

    try:
        sst = SST.from_string(rev.materialize())
    except ValueError as e:
        return HttpResponse(content=force_str(e.message), content_type='text/plain', status='400')
    
    ctx = Context(
        files_path='http://%s/media/dynamic/uploads/%s/' % (request.get_host(), pk),
        source_url='http://%s%s' % (request.get_host(), reverse('catalogue_html', args=[doc.pk])),
    )
    if doc.owner_organization is not None and doc.owner_organization.logo:
        ctx.cover_logo = 'http://%s%s' % (request.get_host(), doc.owner_organization.logo.url)
    try:
        pdf_file = PdfFormat(sst).build(ctx)
    except BuildError as e:
        return HttpResponse(content=force_str(e.message), content_type='text/plain', status='400')

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

    try:
        sst = SST.from_string(rev.materialize())
    except ValueError as e:
        return HttpResponse(content=force_str(e.message), content_type='text/plain', status='400')

    ctx = Context(
        files_path='http://%s/media/dynamic/uploads/%s/' % (request.get_host(), pk),
        source_url='http://%s%s' % (request.get_host(), reverse('catalogue_html', args=[doc.pk])),
    )
    if doc.owner_organization is not None and doc.owner_organization.logo:
        ctx.cover_logo = 'http://%s%s' % (request.get_host(), doc.owner_organization.logo.url)
    try:
        epub_file = EpubFormat(sst).build(ctx)
    except BuildError as e:
        return HttpResponse(content=force_str(e.message), content_type='text/plain', status='400')

    from catalogue.ebook_utils import serve_file
    return serve_file(epub_file.get_filename(), '%d.epub' % doc.pk, 'application/epub+zip')


@never_cache
def book_mobi(request, pk, rev_pk):
    from librarian.utils import Context
    from librarian.document import Document as SST
    from librarian.formats.epub import EpubFormat

    doc = get_object_or_404(Document, pk=pk)
    rev = get_object_or_404(Revision, pk=rev_pk)

    try:
        sst = SST.from_string(rev.materialize())
    except ValueError as e:
        return HttpResponse(content=force_str(e.message), content_type='text/plain', status='400')

    ctx = Context(
        files_path='http://%s/media/dynamic/uploads/%s/' % (request.get_host(), pk),
        source_url='http://%s%s' % (request.get_host(), reverse('catalogue_html', args=[doc.pk])),
    )
    if doc.owner_organization is not None and doc.owner_organization.logo:
        ctx.cover_logo = 'http://%s%s' % (request.get_host(), doc.owner_organization.logo.url)
    try:
        epub_file = EpubFormat(sst).build(ctx)
    except BuildError as e:
        return HttpResponse(content=force_str(e.message), content_type='text/plain', status='400')

    output_file = NamedTemporaryFile(prefix='librarian', suffix='.mobi', delete=False)
    output_file.close()
    subprocess.check_call(
        ['ebook-convert', epub_file.get_filename(), output_file.name, '--no-inline-toc'])

    from catalogue.ebook_utils import serve_file
    return serve_file(output_file.name, '%d.mobi' % doc.pk, 'application/epub+zip')


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
        if not doc.published:
            site = Site.objects.get_current()
            send_notify_email(
                'New published document in MIL/PEER',
                '''New published document in MIL/PEER: %s. View it in browser: https://%s%s.

--
MIL/PEER team.''' % (doc.meta()['title'], site.domain, reverse('catalogue_html', args=[doc.pk])))
        PublishRecord.objects.create(revision=rev, document=doc, user=request.user)
        doc.published = True
        doc.save()
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
