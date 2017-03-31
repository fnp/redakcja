# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import unicode_literals

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

try:
    from gzip import compress, decompress
except ImportError:
    # Python < 3.2
    from gzip import GzipFile
    from StringIO import StringIO

    def compress(data):
        compressed = StringIO()
        GzipFile(fileobj=compressed, mode="wb").write(data)
        return compressed.getvalue()

    def decompress(data):
        return GzipFile(fileobj=StringIO(data)).read()


class GzipFileSystemStorage(FileSystemStorage):
    def _open(self, name, mode='rb'):
        """TODO: This is good for reading; what about writing?"""
        f = open(self.path(name), 'rb')
        text = f.read()
        f.close()
        return ContentFile(decompress(text))

    def _save(self, name, content):
        content = ContentFile(compress(content.read()))
        return super(GzipFileSystemStorage, self)._save(name, content)

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
