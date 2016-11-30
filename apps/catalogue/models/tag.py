# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    label = models.CharField(max_length=64, verbose_name=_('category'))
    dc_tag = models.CharField(max_length=32)
    index = models.IntegerField()

    class Meta:
        ordering = ['index']


class Tag(models.Model):
    label = models.CharField(max_length=64, verbose_name=_('tag'))
    category = models.ForeignKey(Category)
    index = models.IntegerField()

    class Meta:
        ordering = ['index']
