# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from catalogue.models import Chunk


class BookPublishRecord(models.Model):
    """
        A record left after publishing a Book.
    """

    book = models.ForeignKey('Book', verbose_name=_('book'), related_name='publish_log')
    timestamp = models.DateTimeField(_('time'), auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=_('user'))

    class Meta:
        app_label = 'catalogue'
        ordering = ['-timestamp']
        verbose_name = _('book publish record')
        verbose_name_plural = _('book publish records')


class ChunkPublishRecord(models.Model):
    """
        BookPublishRecord details for each Chunk.
    """

    book_record = models.ForeignKey(BookPublishRecord, verbose_name=_('book publish record'))
    change = models.ForeignKey(Chunk.change_model, related_name='publish_log', verbose_name=_('change'))

    class Meta:
        app_label = 'catalogue'
        verbose_name = _('chunk publish record')
        verbose_name_plural = _('chunk publish records')
