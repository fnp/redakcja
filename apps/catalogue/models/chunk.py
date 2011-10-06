# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from catalogue.helpers import cached_in_field
from catalogue.managers import VisibleManager
from catalogue.tasks import refresh_instance
from dvcs import models as dvcs_models


class Chunk(dvcs_models.Document):
    """ An editable chunk of text. Every Book text is divided into chunks. """
    REPO_PATH = settings.CATALOGUE_REPO_PATH

    book = models.ForeignKey('Book', editable=False, verbose_name=_('book'))
    number = models.IntegerField(_('number'))
    slug = models.SlugField(_('slug'))
    title = models.CharField(_('title'), max_length=255, blank=True)
    gallery_start = models.IntegerField(_('gallery start'), null=True, blank=True)

    # cache
    _short_html = models.TextField(null=True, blank=True, editable=False)
    _hidden = models.NullBooleanField(editable=False)
    _changed = models.NullBooleanField(editable=False)

    # managers
    objects = models.Manager()
    visible_objects = VisibleManager()

    class Meta:
        app_label = 'catalogue'
        unique_together = [['book', 'number'], ['book', 'slug']]
        ordering = ['number']
        verbose_name = _('chunk')
        verbose_name_plural = _('chunks')
        permissions = [('can_pubmark', 'Can mark for publishing')]

    # Representing
    # ============

    def __unicode__(self):
        return "%d:%d: %s" % (self.book_id, self.number, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ("wiki_editor", [self.book.slug, self.slug])

    def pretty_name(self, book_length=None):
        title = self.book.title
        if self.title:
            title += ", %s" % self.title
        if book_length > 1:
            title += " (%d/%d)" % (self.number, book_length)
        return title


    # Creating and manipulation
    # =========================

    def split(self, slug, title='', adjust_slug=False, **kwargs):
        """ Create an empty chunk after this one """
        self.book.chunk_set.filter(number__gt=self.number).update(
                number=models.F('number')+1)
        new_chunk = None
        while not new_chunk:
            new_slug = self.book.make_chunk_slug(slug)
            try:
                new_chunk = self.book.chunk_set.create(number=self.number+1,
                    slug=new_slug[:50], title=title[:255], **kwargs)
            except IntegrityError:
                pass
        return new_chunk

    @classmethod
    def get(cls, book_slug, chunk_slug=None):
        if chunk_slug is None:
            return cls.objects.get(book__slug=book_slug, number=1)
        else:
            return cls.objects.get(book__slug=book_slug, slug=chunk_slug)


    # State & cache
    # =============

    def new_publishable(self):
        change = self.publishable()
        if not change:
            return False
        return change.publish_log.exists()

    def is_changed(self):
        if self.head is None:
            return False
        return not self.head.publishable
    changed = cached_in_field('_changed')(is_changed)

    def is_hidden(self):
        return self.book.hidden()
    hidden = cached_in_field('_hidden')(is_hidden)

    @cached_in_field('_short_html')
    def short_html(self):
        return render_to_string(
                    'catalogue/book_list/chunk.html', {'chunk': self})

    def touch(self):
        update = {
            "_changed": self.is_changed(),
            "_hidden": self.is_hidden(),
            "_short_html": None,
        }
        Chunk.objects.filter(pk=self.pk).update(**update)
        refresh_instance(self)

    def refresh(self):
        """This should be done offline."""
        self.changed
        self.hidden
        self.short_html
