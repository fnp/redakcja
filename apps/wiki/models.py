# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
import os
import vstorage
from vstorage import DocumentNotFound
from wiki import settings, constants
from django.utils.translation import ugettext_lazy as _

from django.http import Http404

import logging
logger = logging.getLogger("fnp.wiki")


# _PCHARS_DICT = dict(zip((ord(x) for x in u"ĄĆĘŁŃÓŚŻŹąćęłńóśżź "), u"ACELNOSZZacelnoszz_"))
_PCHARS_DICT = dict(zip((ord(x) for x in u" "), u"_"))

# I know this is barbaric, but I didn't find a better solution ;(
def split_name(name):
    parts = name.translate(_PCHARS_DICT).split('__')
    return parts

def join_name(*parts, **kwargs):
    name = u'__'.join(p.translate(_PCHARS_DICT) for p in parts)
    logger.info("JOIN %r -> %r", parts, name)
    return name

def normalize_name(name):
    """
    >>> normalize_name("gąska".decode('utf-8'))
    u'g\u0105ska'
    """
    return name.translate(_PCHARS_DICT).lower()

STAGE_TAGS_RE = re.compile(r'^#stage-finished: (.*)$', re.MULTILINE)


class DocumentStorage(object):
    def __init__(self, path):
        self.vstorage = vstorage.VersionedStorage(path)

    def get(self, name, revision=None):
        text, rev = self.vstorage.page_text(name, revision)
        return Document(self, name=name, text=text, revision=rev)

    def get_by_tag(self, name, tag):
        text, rev = self.vstorage.page_text_by_tag(name, tag)
        return Document(self, name=name, text=text, revision=rev)

    def revert(self, name, revision):
        text, rev = self.vstorage.revert(name, revision)
        return Document(self, name=name, text=text, revision=rev)

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except DocumentNotFound:
            raise Http404

    def put(self, document, author, comment, parent=None):
        self.vstorage.save_text(
                title=document.name,
                text=document.text,
                author=author,
                comment=comment,
                parent=parent)

        return document

    def create_document(self, text, name):
        title = u', '.join(p.title for p in split_name(name))

        if text is None:
            text = u''

        document = Document(self, name=name, text=text, title=title)
        return self.put(document, u"<wiki>", u"Document created.")

    def delete(self, name, author, comment):
        self.vstorage.delete_page(name, author, comment)

    def all(self):
        return list(self.vstorage.all_pages())

    def history(self, title):
        def stage_desc(match):
            stage = match.group(1)
            return _("Finished stage: %s") % constants.DOCUMENT_STAGES_DICT[stage]

        for changeset in self.vstorage.page_history(title):
            changeset['description'] = STAGE_TAGS_RE.sub(stage_desc, changeset['description'])
            yield changeset



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
        return result

    def info(self):
        return self.storage.vstorage.page_meta(self.name, self.revision)

def getstorage():
    return DocumentStorage(settings.REPOSITORY_PATH)

#
# Django models
#
