# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from documents.helpers import cached_in_field
from documents.managers import VisibleManager
from dvcs import models as dvcs_models


class Chunk(dvcs_models.Document):
    """ An editable chunk of text. Every Book text is divided into chunks. """
    REPO_PATH = settings.CATALOGUE_REPO_PATH

    book = models.ForeignKey('Book', models.CASCADE, editable=False, verbose_name=_('book'))
    number = models.IntegerField(_('number'))
    title = models.CharField(_('title'), max_length=255, blank=True)
    slug = models.SlugField(_('slug'))
    gallery_start = models.IntegerField(_('gallery start'), null=True, blank=True, default=1)

    # cache
    _hidden = models.BooleanField(editable=False, null=True)
    _changed = models.BooleanField(editable=False, null=True)
    _new_publishable = models.BooleanField(editable=False, null=True)

    # managers
    objects = models.Manager()
    visible_objects = VisibleManager()

    class Meta:
        app_label = 'documents'
        unique_together = [['book', 'number'], ['book', 'slug']]
        ordering = ['number']
        verbose_name = _('chunk')
        verbose_name_plural = _('chunks')
        permissions = [('can_pubmark', 'Can mark for publishing')]

    @classmethod
    def get_visible_for(cls, user):
        qs = cls.objects.all()
        if not user.is_authenticated:
            qs = qs.filter(book__public=True)
        return qs

    @classmethod
    def get_revisions_visible_for(cls, user):
        qs = cls.change_model.objects.all()
        if not user.is_authenticated:
            qs = qs.filter(tree__book__public=True)
        return qs
    
    # Representing
    # ============

    def __str__(self):
        return "%d:%d: %s" % (self.book_id, self.number, self.title)

    def get_absolute_url(self):
        return reverse("wiki_editor", args=[self.book.slug, self.slug])

    def pretty_name(self, book_length=None):
        title = self.book.title
        if self.title:
            title += ", %s" % self.title
        if book_length and book_length > 1:
            title += " (%d/%d)" % (self.number, book_length)
        return title

    # Creating and manipulation
    # =========================

    def split(self, slug, title='', **kwargs):
        """ Create an empty chunk after this one """
        # Single update makes unique constr choke on postgres.
        for chunk in self.book.chunk_set.filter(number__gt=self.number).order_by('-number'):
            chunk.number += 1
            chunk.save()
        new_chunk = None
        while not new_chunk:
            new_slug = self.book.make_chunk_slug(slug)
            try:
                new_chunk = self.book.chunk_set.create(
                    number=self.number+1,
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

    def is_new_publishable(self):
        change = self.publishable()
        if not change:
            return False
        return not change.publish_log.exists()
    new_publishable = cached_in_field('_new_publishable')(is_new_publishable)

    def is_changed(self):
        if self.head is None:
            return False
        return not self.head.publishable
    changed = cached_in_field('_changed')(is_changed)

    def is_hidden(self):
        return self.book.hidden()
    hidden = cached_in_field('_hidden')(is_hidden)

    def touch(self):
        update = {
            "_changed": self.is_changed(),
            "_new_publishable": self.is_new_publishable(),
            "_hidden": self.is_hidden(),
        }
        Chunk.objects.filter(pk=self.pk).update(**update)
