# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import itertools
import re

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from dvcs import models as dvcs_models
from wiki.xml_tools import compile_text

import logging
logger = logging.getLogger("fnp.wiki")


class Book(models.Model):
    """ A document edited on the wiki """

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=128, unique=True)
    gallery = models.CharField(_('scan gallery name'), max_length=255, blank=True)

    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_('parent'), related_name="children")
    parent_number = models.IntegerField(_('parent number'), null=True, blank=True, db_index=True)

    _list_html = models.TextField(editable=False, null=True)

    class NoTextError(BaseException):
        pass

    class Meta:
        ordering = ['parent_number', 'title']
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("wiki_book", args=[self.slug])

    def save(self, reset_list_html=True, *args, **kwargs):
        if reset_list_html:
            self._list_html = None
        return super(Book, self).save(*args, **kwargs)

    @classmethod
    def create(cls, creator=None, text=u'', *args, **kwargs):
        """
            >>> Book.create(slug='x', text='abc').materialize()
            'abc'
        """
        instance = cls(*args, **kwargs)
        instance.save()
        instance[0].commit(author=creator, text=text)
        return instance

    def __iter__(self):
        return iter(self.chunk_set.all())

    def __getitem__(self, chunk):
        return self.chunk_set.all()[chunk]

    def __len__(self):
        return self.chunk_set.count()

    def list_html(self):
        if self._list_html is None:
            print 'rendering', self.title
            self._list_html = render_to_string('wiki/document_list_item.html',
                {'book': self})
            self.save(reset_list_html=False)
        return mark_safe(self._list_html)

    @staticmethod
    def publish_tag():
        return dvcs_models.Tag.get('publish')

    def materialize(self, tag=None):
        """ 
            Get full text of the document compiled from chunks.
            Takes the current versions of all texts
            or versions most recently tagged by a given tag.
        """
        if tag:
            changes = [chunk.last_tagged(tag) for chunk in self]
        else:
            changes = [chunk.head for chunk in self]
        if None in changes:
            raise self.NoTextError('Some chunks have no available text.')
        return compile_text(change.materialize() for change in changes)

    def publishable(self):
        if not len(self):
            return False
        for chunk in self:
            if not chunk.publishable():
                return False
        return True

    def make_chunk_slug(self, proposed):
        """ 
            Finds a chunk slug not yet used in the book.
        """
        slugs = set(c.slug for c in self)
        i = 1
        new_slug = proposed
        while new_slug in slugs:
            new_slug = "%s-%d" % (proposed, i)
            i += 1
        return new_slug

    def append(self, other):
        number = self[len(self) - 1].number + 1
        single = len(other) == 1
        for chunk in other:
            # move chunk to new book
            chunk.book = self
            chunk.number = number

            # try some title guessing
            if other.title.startswith(self.title):
                other_title_part = other.title[len(self.title):].lstrip(' /')
            else:
                other_title_part = other.title

            if single:
                # special treatment for appending one-parters:
                # just use the guessed title and original book slug
                chunk.comment = other_title_part
                if other.slug.startswith(self.slug):
                    chunk_slug = other.slug[len(self.slug):].lstrip('-_')
                else:
                    chunk_slug = other.slug
                chunk.slug = self.make_chunk_slug(chunk_slug)
            else:
                chunk.comment = "%s, %s" % (other_title_part, chunk.comment)
                chunk.slug = self.make_chunk_slug(chunk.slug)
            chunk.save()
            number += 1
        other.delete()

    @staticmethod
    def listener_create(sender, instance, created, **kwargs):
        if created:
            instance.chunk_set.create(number=1, slug='1')

models.signals.post_save.connect(Book.listener_create, sender=Book)


class Chunk(dvcs_models.Document):
    """ An editable chunk of text. Every Book text is divided into chunks. """

    book = models.ForeignKey(Book, editable=False)
    number = models.IntegerField()
    slug = models.SlugField()
    comment = models.CharField(max_length=255)

    class Meta:
        unique_together = [['book', 'number'], ['book', 'slug']]
        ordering = ['number']

    def __unicode__(self):
        return "%d-%d: %s" % (self.book_id, self.number, self.comment)

    def get_absolute_url(self):
        return reverse("wiki_editor", args=[self.book.slug, self.slug])

    @classmethod
    def get(cls, slug, chunk=None):
        if chunk is None:
            return cls.objects.get(book__slug=slug, number=1)
        else:
            return cls.objects.get(book__slug=slug, slug=chunk)

    def pretty_name(self):
        return "%s, %s (%d/%d)" % (self.book.title, self.comment, 
                self.number, len(self.book))

    def publishable(self):
        return self.last_tagged(Book.publish_tag())

    def split(self, slug, comment='', creator=None):
        """ Create an empty chunk after this one """
        self.book.chunk_set.filter(number__gt=self.number).update(
                number=models.F('number')+1)
        new_chunk = self.book.chunk_set.create(number=self.number+1,
                creator=creator, slug=slug, comment=comment)
        return new_chunk

    @staticmethod
    def listener_saved(sender, instance, created, **kwargs):
        if instance.book:
            # save book so that its _list_html is reset
            instance.book.save()

models.signals.post_save.connect(Chunk.listener_saved, sender=Chunk)


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

