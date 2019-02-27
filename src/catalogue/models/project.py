# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):
    """ A project, tracked for funding purposes. """

    name = models.CharField(_('name'), max_length=255, unique=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    class Meta:
        app_label = 'catalogue'
        ordering = ['name']
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __unicode__(self):
        return self.name
