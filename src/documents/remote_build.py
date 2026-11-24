# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import requests
from django.conf import settings
from documents.models import Book


def gather_files(book, publishable=True):
    files = []
    todo = [book]
    while todo:
        b = todo.pop()
        xml = book.materialize(publishable=publishable)
        files.append((
            'doc' if b == book else 'part',
            (b.dc_slug + '.xml', xml, 'application/xml')
        ))
        for part in b.wldocument(publishable=publishable).book_info.parts:
            todo.push(Book.objects.get(dc_slug=part.slug))
    return files


def remote_build(book, fmt, publishable=True, options=None, content=None):
    if not settings.REMOTE_BUILD_URL or not settings.REMOTE_BUILD_TOKEN:
        raise RuntimeError('Remote build not configured')

    if book is None:
        assert content
        files = [('doc', ('doc.xml', content, 'application/xml'))]
    else:
        files = gather_files(book, publishable=publishable)

    if options:
        options = json.dumps(options)
    response = requests.post(
        settings.REMOTE_BUILD_URL + '/build/pdf',
        headers={'Authorization': 'Bearer ' + settings.REMOTE_BUILD_TOKEN},
        files=files,
        data={'options': options}
    )
    if response.status_code != 200:
        try:
            error = response.json()
        except ValueError:
            error = {'error': response.text}
        message = '%d: %s' % (response.status_code, error.get('error'))
        if error.get('log'):
            message += '\n' + error['log']
        raise RuntimeError(message)
    return response.content
