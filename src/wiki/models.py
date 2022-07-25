# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import gettext_lazy as _

import logging
logger = logging.getLogger("fnp.wiki")


class Theme(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('theme')
        verbose_name_plural = _('themes')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Theme(name=%r)" % self.name

