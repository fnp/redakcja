# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import itertools
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from dvcs import models as dvcs_models


import logging
logger = logging.getLogger("fnp.wiki")


RE_TRIM_BEGIN = re.compile("^<!-- TRIM_BEGIN -->$", re.M)
RE_TRIM_END = re.compile("^<!-- TRIM_END -->$", re.M)


class Book(models.Model):
    """ A document edited on the wiki """

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=128, unique=True)
    gallery = models.CharField(_('scan gallery name'), max_length=255, blank=True)

    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_('parent'), related_name="children")
    parent_number = models.IntegerField(_('parent number'), null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['parent_number', 'title']
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __unicode__(self):
        return self.title

    @classmethod
    def create(cls, creator=None, text=u'', *args, **kwargs):
        """
            >>> Book.create(slug='x', text='abc').materialize()
            'abc'
        """
        instance = cls(*args, **kwargs)
        instance.save()
        instance.chunk_set.all()[0].doc.commit(author=creator, text=text)
        return instance

    @staticmethod
    def trim(text, trim_begin=True, trim_end=True):
        """ 
            Cut off everything before RE_TRIM_BEGIN and after RE_TRIM_END, so
            that eg. one big XML file can be compiled from many small XML files.
        """
        if trim_begin:
            text = RE_TRIM_BEGIN.split(text, maxsplit=1)[-1]
        if trim_end:
            text = RE_TRIM_END.split(text, maxsplit=1)[0]
        return text

    def materialize(self):
        """ 
            Get full text of the document compiled from chunks.
            Takes the current versions of all texts for now, but it should
            be possible to specify a tag or a point in time for compiling.

            First non-empty text's beginning isn't trimmed,
            and last non-empty text's end isn't trimmed.
        """
        texts = []
        trim_begin = False
        text = ''
        for chunk in self.chunk_set.all():
            next_text = chunk.doc.materialize()
            if not next_text:
                continue
            if text:
                # trim the end, because there's more non-empty text
                # don't trim beginning, if `text' is the first non-empty part
                texts.append(self.trim(text, trim_begin=trim_begin))
                trim_begin = True
            text = next_text
        # don't trim the end, because there's no more text coming after `text'
        # only trim beginning if it's not still the first non-empty
        texts.append(self.trim(text, trim_begin=trim_begin, trim_end=False))
        return "".join(texts)

    @staticmethod
    def listener_create(sender, instance, created, **kwargs):
        if created:
            instance.chunk_set.create(number=1, slug='1')

models.signals.post_save.connect(Book.listener_create, sender=Book)


class Chunk(models.Model):
    """ An editable chunk of text. Every Book text is divided into chunks. """

    book = models.ForeignKey(Book)
    number = models.IntegerField()
    slug = models.SlugField()
    comment = models.CharField(max_length=255)
    doc = models.ForeignKey(dvcs_models.Document, editable=False, unique=True, null=True)

    class Meta:
        unique_together = [['book', 'number'], ['book', 'slug']]
        ordering = ['number']

    def __unicode__(self):
        return "%d-%d: %s" % (self.book_id, self.number, self.comment)

    def save(self, *args, **kwargs):
        if self.doc is None:
            self.doc = dvcs_models.Document.objects.create()
        super(Chunk, self).save(*args, **kwargs)

    @classmethod
    def get(cls, slug, chunk=None):
        if chunk is None:
            return cls.objects.get(book__slug=slug, number=1)
        else:
            return cls.objects.get(book__slug=slug, slug=chunk)

    def pretty_name(self):
        return "%s, %s (%d/%d)" % (self.book.title, self.comment, 
                self.number, self.book.chunk_set.count())




'''
from wiki import settings, constants
from slughifi import slughifi

from django.http import Http404




class Document(object):

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

        gallery = result.get('gallery', slughifi(self.name.replace(' ', '_')))

        if gallery.startswith('/'):
            gallery = os.path.basename(gallery)

        result['gallery'] = gallery
        return result

    def info(self):
        return self.storage.vstorage.page_meta(self.name, self.revision)



'''
class Theme(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('theme')
        verbose_name_plural = _('themes')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Theme(name=%r)" % self.name

