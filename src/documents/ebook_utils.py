# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from io import BytesIO
from .models import Book
from librarian import DocProvider
from django.http import HttpResponse


class RedakcjaDocProvider(DocProvider):
    """Used for getting books' children."""

    def __init__(self, publishable):
        self.publishable = publishable

    def by_slug(self, slug):
        return BytesIO(Book.objects.get(catalogue_book_id=slug
                    ).materialize(publishable=self.publishable
                    ).encode('utf-8'))


def serve_file(file_path, name, mime_type):
    def read_chunks(f, size=8192):
        chunk = f.read(size)
        while chunk:
            yield chunk
            chunk = f.read(size)

    response = HttpResponse(content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % name
    with open(file_path, 'rb') as f:
        for chunk in read_chunks(f):
            response.write(chunk)
    return response
