# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.utils import IntegrityError

from slughifi import slughifi

from dvcs import models as dvcs_models
from catalogue.xml_tools import compile_text, split_xml

import logging
logger = logging.getLogger("fnp.catalogue")


class Book(models.Model):
    """ A document edited on the wiki """

    title = models.CharField(_('title'), max_length=255, db_index=True)
    slug = models.SlugField(_('slug'), max_length=128, unique=True, db_index=True)
    gallery = models.CharField(_('scan gallery name'), max_length=255, blank=True)

    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_('parent'), related_name="children")
    parent_number = models.IntegerField(_('parent number'), null=True, blank=True, db_index=True)

    class NoTextError(BaseException):
        pass

    class Meta:
        ordering = ['parent_number', 'title']
        verbose_name = _('book')
        verbose_name_plural = _('books')
        permissions = [('can_pubmark', 'Can mark for publishing')]

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("catalogue_book", args=[self.slug])

    @classmethod
    def import_xml_text(cls, text=u'', creator=None, previous_book=None,
                *args, **kwargs):

        texts = split_xml(text)
        if previous_book:
            instance = previous_book
        else:
            instance = cls(*args, **kwargs)
            instance.save()

        # if there are more parts, set the rest to empty strings
        book_len = len(instance)
        for i in range(book_len - len(texts)):
            texts.append(u'pusta część %d' % (i + 1), u'')

        i = 0
        for i, (title, text) in enumerate(texts):
            if not title:
                title = u'część %d' % (i + 1)

            slug = slughifi(title)

            if i < book_len:
                chunk = instance[i]
                chunk.slug = slug
                chunk.comment = title
                chunk.save()
            else:
                chunk = instance.add(slug, title, creator, adjust_slug=True)

            chunk.commit(text, author=creator)

        return instance

    @classmethod
    def create(cls, creator=None, text=u'', *args, **kwargs):
        """
            >>> Book.create(slug='x', text='abc').materialize()
            'abc'
        """
        instance = cls(*args, **kwargs)
        instance.save()
        instance[0].commit(text, author=creator)
        return instance

    def __iter__(self):
        return iter(self.chunk_set.all())

    def __getitem__(self, chunk):
        return self.chunk_set.all()[chunk]

    def __len__(self):
        return self.chunk_set.count()

    def __nonzero__(self):
        """
            Necessary so that __len__ isn't used for bool evaluation.
        """
        return True

    def get_current_changes(self, publishable=True):
        """
            Returns a list containing one Change for every Chunk in the Book.
            Takes the most recent revision (publishable, if set).
            Throws an error, if a proper revision is unavailable for a Chunk.
        """
        if publishable:
            changes = [chunk.publishable() for chunk in self]
        else:
            changes = [chunk.head for chunk in self if chunk.head is not None]
        if None in changes:
            raise self.NoTextError('Some chunks have no available text.')
        return changes

    def materialize(self, publishable=False, changes=None):
        """ 
            Get full text of the document compiled from chunks.
            Takes the current versions of all texts
            or versions most recently tagged for publishing,
            or a specified iterable changes.
        """
        if changes is None:
            changes = self.get_current_changes(publishable)
        return compile_text(change.materialize() for change in changes)

    def publishable(self):
        if not self.chunk_set.exists():
            return False
        for chunk in self:
            if not chunk.publishable():
                return False
        return True

    def publish(self, user):
        """
            Publishes a book on behalf of a (local) user.
        """
        from apiclient import api_call

        changes = self.get_current_changes(publishable=True)
        book_xml = book.materialize(changes=changes)
        #api_call(user, "books", {"book_xml": book_xml})
        # record the publish
        br = BookPublishRecord.objects.create(book=self, user=user)
        for c in changes:
            ChunkPublishRecord.objects.create(book_record=br, change=c)

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
        """Add all chunks of another book to self."""
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

    def add(self, *args, **kwargs):
        """Add a new chunk at the end."""
        return self.chunk_set.reverse()[0].split(*args, **kwargs)

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
    comment = models.CharField(max_length=255, blank=True)

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

    def pretty_name(self, book_length=None):
        title = self.book.title
        if self.comment:
            title += ", %s" % self.comment
        if book_length > 1:
            title += " (%d/%d)" % (self.number, book_length)
        return title

    def split(self, slug, comment='', creator=None, adjust_slug=False):
        """ Create an empty chunk after this one """
        self.book.chunk_set.filter(number__gt=self.number).update(
                number=models.F('number')+1)
        tries = 1
        new_slug = slug
        new_chunk = None
        while not new_chunk:
            try:
                new_chunk = self.book.chunk_set.create(number=self.number+1,
                    creator=creator, slug=new_slug, comment=comment)
            except IntegrityError:
                if not adjust_slug:
                    raise
                new_slug = "%s_%d" % (slug, tries)
                tries += 1
        return new_chunk

    @staticmethod
    def listener_saved(sender, instance, created, **kwargs):
        if instance.book:
            # save book so that its _list_html is reset
            instance.book.save()

models.signals.post_save.connect(Chunk.listener_saved, sender=Chunk)


class BookPublishRecord(models.Model):
    """
        A record left after publishing a Book.
    """

    book = models.ForeignKey(Book)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ['-timestamp']


class ChunkPublishRecord(models.Model):
    """
        BookPublishRecord details for each Chunk.
    """

    book_record = models.ForeignKey(BookPublishRecord)
    change = models.ForeignKey(Chunk.change_model)
