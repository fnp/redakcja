# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from catalogue.helpers import cached_in_field
from catalogue.tasks import refresh_instance
from dvcs import models as dvcs_models


class Image(dvcs_models.Document):
    """ An editable chunk of text. Every Book text is divided into chunks. """
    REPO_PATH = settings.CATALOGUE_IMAGE_REPO_PATH

    image = models.FileField(_('image'), upload_to='catalogue/images')
    title = models.CharField(_('title'), max_length=255, blank=True)
    slug = models.SlugField(_('slug'), unique=True)
    public = models.BooleanField(_('public'), default=True, db_index=True)

    # cache
    _short_html = models.TextField(null=True, blank=True, editable=False)
    _new_publishable = models.NullBooleanField(editable=False)
    _published = models.NullBooleanField(editable=False)
    _changed = models.NullBooleanField(editable=False)

    class Meta:
        app_label = 'catalogue'
        ordering = ['title']
        verbose_name = _('image')
        verbose_name_plural = _('images')
        permissions = [('can_pubmark_image', 'Can mark images for publishing')]

    # Representing
    # ============

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ("catalogue_image", [self.slug])

    # State & cache
    # =============

    def accessible(self, request):
        return self.public or request.user.is_authenticated()

    def is_new_publishable(self):
        change = self.publishable()
        if not change:
            return False
        return change.publish_log.exists()
    new_publishable = cached_in_field('_new_publishable')(is_new_publishable)

    def is_published(self):
        return self.publish_log.exists()
    published = cached_in_field('_published')(is_published)

    def is_changed(self):
        if self.head is None:
            return False
        return not self.head.publishable
    changed = cached_in_field('_changed')(is_changed)

    @cached_in_field('_short_html')
    def short_html(self):
        return render_to_string(
                    'catalogue/image_short.html', {'image': self})

    def refresh(self):
        """This should be done offline."""
        self.short_html
        self.single
        self.new_publishable
        self.published

    def touch(self):
        update = {
            "_changed": self.is_changed(),
            "_short_html": None,
            "_new_publishable": self.is_new_publishable(),
            "_published": self.is_published(),
        }
        Image.objects.filter(pk=self.pk).update(**update)
        refresh_instance(self)

    def refresh(self):
        """This should be done offline."""
        self.changed
        self.short_html
