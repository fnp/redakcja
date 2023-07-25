# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from hashlib import sha1
from os import makedirs
import os.path
import PIL.Image
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from lxml import etree
from librarian import RDFNS, DCNS
from librarian.cover import make_cover
from librarian.dcparser import BookInfo
from documents.helpers import active_tab
from documents.models import Book, Chunk
from cover.models import Image
from cover import forms
from cover.utils import get_import_data


PREVIEW_SIZE = (212, 300)


def preview(request, book, chunk=None, rev=None):
    """Creates a cover image.

    If chunk and rev number are given, use version from given revision.
    If rev is not given, use publishable version.
    """
    try:
        chunk = Chunk.get(book, chunk)
    except Chunk.DoesNotExist:
        raise Http404

    if chunk.book.cover and rev is None and not request.GET.get('width') and not request.GET.get('height'):
        return HttpResponseRedirect(chunk.book.cover.url)

    if rev is not None:
        try:
            revision = chunk.at_revision(rev)
        except Chunk.change_model.DoesNotExist:
            raise Http404
    else:
        revision = chunk.publishable()
        if revision is None:
            revision = chunk.head
    xml = revision.materialize().encode('utf-8')

    try:
        info = BookInfo.from_bytes(xml)
    except Exception as e:
        print(e)
        return HttpResponseRedirect(os.path.join(settings.STATIC_URL, "img/sample_cover.png"))
    width = request.GET.get('width')
    width = int(width) if width else None
    height=request.GET.get('height')
    height = int(height) if height else None

    if not (height or width):
        width, height = PREVIEW_SIZE

    cover_class = request.GET.get('cover_class', 'default')

    cover = make_cover(info, cover_class=cover_class, width=width, height=height)
    response = HttpResponse(content_type=cover.mime_type())
    img = cover.final_image()
    img.save(response, cover.format)

    if 'download' in request.GET:
        response['Content-Disposition'] = 'attachment; filename=%s.jpg' % chunk.book.slug

    return response


@csrf_exempt
@require_POST
def preview_from_xml(request):
    xml = request.POST['xml']
    try:
        info = BookInfo.from_bytes(xml.encode('utf-8'))
    except Exception as e:
        print(e)
        return HttpResponse(os.path.join(settings.STATIC_URL, "img/sample_cover.png"))
    coverid = sha1(etree.tostring(info.to_etree())).hexdigest()
    cover = make_cover(info)

    cover_dir = 'cover/preview'
    try:
        makedirs(os.path.join(settings.MEDIA_ROOT, cover_dir))
    except OSError:
        pass
    fname = os.path.join(cover_dir, "%s.%s" % (coverid, cover.ext()))
    img = cover.image().resize(PREVIEW_SIZE, PIL.Image.ANTIALIAS)
    img.save(os.path.join(settings.MEDIA_ROOT, fname))
    return HttpResponse(os.path.join(settings.MEDIA_URL, fname))


@active_tab('cover')
def image(request, pk):
    img = get_object_or_404(Image, pk=pk)

    if not request.accepts('text/html') and request.accepts('application/json') or request.GET.get('format') == 'json':
        return JsonResponse({
            'attribution': img.attribution,
            'cut_left': img.cut_left,
            'cut_right': img.cut_right,
            'cut_top': img.cut_top,
            'cut_bottom': img.cut_bottom,
            'file': img.file.url,
            'use_file': img.use_file.url,
        })

    if request.user.has_perm('cover.change_image'):
        if request.method == "POST":
            form = forms.ImageEditForm(request.POST, request.FILES, instance=img)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(img.get_absolute_url())
        else:
            form = forms.ImageEditForm(instance=img)
        editable = True
    else:
        form = forms.ReadonlyImageEditForm(instance=img)
        editable = False

    return render(request, "cover/image_detail.html", {
        "object": Image.objects.get(id=img.id),
        "form": form,
        "editable": editable,
    })


def image_file(request, pk):
    img = get_object_or_404(Image, pk=pk)
    return HttpResponseRedirect(img.file.url)


@active_tab('cover')
def image_list(request):
    return render(request, "cover/image_list.html", {
        'object_list': Image.objects.all().order_by('-id'),
        'can_add': request.user.has_perm('cover.add_image'),
    })


@permission_required('cover.add_image')
@active_tab('cover')
def add_image(request):
    form = ff = None
    if request.method == 'POST':
        if request.POST.get('form_id') == 'import':
            ff = forms.ImportForm(request.POST)
            if ff.is_valid():
                form = forms.ImageAddForm(ff.cleaned_data)
        else:
            form = forms.ImageAddForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save()
                return HttpResponseRedirect(obj.get_absolute_url())
    if form is None:
        form = forms.ImageAddForm()
    if ff is None:
        ff = forms.ImportForm()
    return render(request, 'cover/add_image.html', {
            'form': form,
            'ff': ff,
        })

@permission_required('cover.add_image')
def quick_import(request, pk):
    url = request.POST.get('url')
    if url.startswith('%s://%s/' % (
            request.scheme,
            request.get_host())):
        cover_id = url.rstrip('/').rsplit('/', 1)[-1]
        cover = Image.objects.get(pk=cover_id)
    else:
        data = get_import_data(url)
        same = Image.objects.filter(source_url=data['source_url'])
        if not same.exists():
            same = Image.objects.filter(download_url=data['download_url'])
        if same.exists():
            cover = same.first()
        else:
            form = forms.ImageAddForm(data)
            if form.is_valid():
                cover = form.save()

    # We have a cover. Now let's commit.
    book = Book.objects.get(pk=pk)
    chunk = book[0]
    text = chunk.head.materialize()

    root = etree.fromstring(text)
    rdf = root.find('.//' + RDFNS('Description'))
    for tag in 'url', 'attribution', 'source':
        for elem in rdf.findall('.//' + DCNS('relation.coverImage.%s' % tag)):
            rdf.remove(elem)
    e = etree.Element(DCNS('relation.coverImage.url'))
    e.text = request.build_absolute_uri(cover.use_file.url)
    rdf.append(e)
    e.tail = '\n    '
    e = etree.Element(DCNS('relation.coverImage.attribution'))
    e.text = ''
    if cover.title:
        e.text += cover.title + ', '
    if cover.author:
        e.text += cover.author + ', '
    e.text += cover.license_name
    e.tail = '\n    '
    rdf.append(e)
    e = etree.Element(DCNS('relation.coverImage.source'))
    e.text = cover.get_full_url()
    e.tail = '\n    '
    rdf.append(e)

    xml = etree.tostring(root, encoding='unicode')
    chunk.commit(
        xml,
        author=request.user,
        comment='Cover',
        publishable=chunk.head.publishable,
    )
    return HttpResponseRedirect(book.get_absolute_url())
        
