# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """ A project, tracked for funding purposes. """

    name = models.CharField(_('name'), max_length=255, unique=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    logo = models.FileField(upload_to='projects', blank=True)
    logo_mono = models.FileField(upload_to='logo_mono', help_text='white on transparent', blank=True)
    logo_alt = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'documents'
        ordering = ['name']
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.name
