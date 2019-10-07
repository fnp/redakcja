# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from catalogue.models import Chunk, Image


class BookPublishRecord(models.Model):
    """
        A record left after publishing a Book.
    """

    book = models.ForeignKey('Book', models.CASCADE, verbose_name=_('book'), related_name='publish_log')
    timestamp = models.DateTimeField(_('time'), auto_now_add=True)
    user = models.ForeignKey(User, models.CASCADE, verbose_name=_('user'))

    class Meta:
        app_label = 'catalogue'
        ordering = ['-timestamp']
        verbose_name = _('book publish record')
        verbose_name_plural = _('book publish records')


class ChunkPublishRecord(models.Model):
    """
        BookPublishRecord details for each Chunk.
    """

    book_record = models.ForeignKey(BookPublishRecord, models.CASCADE, verbose_name=_('book publish record'))
    change = models.ForeignKey(Chunk.change_model, models.CASCADE, related_name='publish_log', verbose_name=_('change'))

    class Meta:
        app_label = 'catalogue'
        verbose_name = _('chunk publish record')
        verbose_name_plural = _('chunk publish records')


class ImagePublishRecord(models.Model):
    """A record left after publishing an Image."""

    image = models.ForeignKey(Image, models.CASCADE, verbose_name=_('image'), related_name='publish_log')
    timestamp = models.DateTimeField(_('time'), auto_now_add=True)
    user = models.ForeignKey(User, models.CASCADE, verbose_name=_('user'))
    change = models.ForeignKey(Image.change_model, models.CASCADE, related_name='publish_log', verbose_name=_('change'))

    class Meta:
        app_label = 'catalogue'
        ordering = ['-timestamp']
        verbose_name = _('image publish record')
        verbose_name_plural = _('image publish records')
