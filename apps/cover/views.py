# Create your views here.
import os.path
from django.conf import settings
from django.http import HttpResponse, Http404
from catalogue.models import Chunk
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


PREVIEW_SIZE = (216, 300)

def preview(request, book, chunk=None, rev=None):
    """Creates a cover image.

    If chunk and rev number are given, use version from given revision.
    If rev is not given, use publishable version.
    """
    import Image
    from librarian.cover import WLCover
    from librarian.dcparser import BookInfo

    chunk = Chunk.get(book, chunk)
    if rev is not None:
        try:
            revision = chunk.at_revision(rev)
        except Chunk.change_model.DoesNotExist:
            raise Http404
    else:
        revision = chunk.publishable()
        if revision is None:
            raise Http404
    xml = revision.materialize().encode('utf-8')
    
    info = BookInfo.from_string(xml)
    cover = WLCover(info)
    response = HttpResponse(mimetype=cover.mime_type())
    image = cover.image().resize(PREVIEW_SIZE, Image.ANTIALIAS)
    image.save(response, cover.format)
    return response


@csrf_exempt
@require_POST
def preview_from_xml(request):
    from hashlib import sha1
    import Image
    from os import makedirs
    from lxml import etree
    from librarian.cover import WLCover
    from librarian.dcparser import BookInfo

    xml = request.POST['xml']
    info = BookInfo.from_string(xml.encode('utf-8'))
    coverid = sha1(etree.tostring(info.to_etree())).hexdigest()
    cover = WLCover(info)

    cover_dir = 'cover/preview'
    try:
        makedirs(os.path.join(settings.MEDIA_ROOT, cover_dir))
    except OSError:
        pass
    fname = os.path.join(cover_dir, "%s.%s" % (coverid, cover.ext()))
    image = cover.image().resize(PREVIEW_SIZE, Image.ANTIALIAS)
    image.save(os.path.join(settings.MEDIA_ROOT, fname))
    return HttpResponse(os.path.join(settings.MEDIA_URL, fname))
