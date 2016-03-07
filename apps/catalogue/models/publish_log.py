# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dvcs.models import Revision


class PublishRecord(models.Model):
    """A record left after publishing a Document."""

    document = models.ForeignKey('Document', verbose_name=_('document'), related_name='publish_log')
    revision = models.ForeignKey(Revision, verbose_name=_('revision'), related_name='publish_log')
    timestamp = models.DateTimeField(_('time'), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('book publish record')
        verbose_name = _('book publish records')
