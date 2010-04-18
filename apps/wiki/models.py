# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
import os
import vstorage
from vstorage import DocumentNotFound
from wiki import settings

from django.http import Http404

import logging
logger = logging.getLogger("fnp.wiki")


class DocumentStorage(object):
    def __init__(self, path):
        self.vstorage = vstorage.VersionedStorage(path)

    def get(self, name, revision=None):
        text, rev = self.vstorage.page_text(name, revision)
        return Document(self, name=name, text=text, revision=rev)

    def get_by_tag(self, name, tag):
        text, rev = self.vstorage.page_text_by_tag(name, tag)
        return Document(self, name=name, text=text, revision=rev)

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except DocumentNotFound:
            raise Http404

    def put(self, document, author, comment, parent):
        self.vstorage.save_text(
                title=document.name,
                text=document.text,
                author=author,
                comment=comment,
                parent=parent)

        return document

    def create_document(self, id, text, title=None):
        if title is None:
            title = id.title()

        if text is None:
            text = u''

        document = Document(self, name=id, text=text, title=title)
        return self.put(document, u"<wiki>", u"Document created.", None)

    def delete(self, name, author, comment):
        self.vstorage.delete_page(name, author, comment)

    def all(self):
        return list(self.vstorage.all_pages())

    def history(self, title):
        return list(self.vstorage.page_history(title))


class Document(object):
    META_REGEX = re.compile(r'\s*<!--\s(.*?)-->', re.DOTALL | re.MULTILINE)

    def __init__(self, storage, **kwargs):
        self.storage = storage
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def add_tag(self, tag, revision, author):
        """ Add document specific tag """
        logger.debug("Adding tag %s to doc %s version %d", tag, self.name, revision)
        self.storage.vstorage.add_page_tag(self.name, revision, tag, user=author)

    @property
    def plain_text(self):
        return re.sub(self.META_REGEX, '', self.text, 1)

    def meta(self):
        result = {}

        m = re.match(self.META_REGEX, self.text)
        if m:
            for line in m.group(1).split('\n'):
                try:
                    k, v = line.split(':', 1)
                    result[k.strip()] = v.strip()
                except ValueError:
                    continue

        gallery = result.get('gallery', self.name.replace(' ', '_'))

        if gallery.startswith('/'):
            gallery = os.path.basename(gallery)

        result['gallery'] = gallery

        if 'title' not in result:
            result['title'] = self.name.title()

        return result

    def info(self):
        return self.storage.vstorage.page_meta(self.name, self.revision)


def getstorage():
    return DocumentStorage(settings.REPOSITORY_PATH)
