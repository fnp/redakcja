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
    multiple = models.BooleanField(default=False, verbose_name=_('multiple choice'))
    tutorial = models.CharField(max_length=250, blank=True)
    index = models.IntegerField()

    class Meta:
        ordering = ['index']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def set_tags_for(self, obj, tags):
        obj.tags.remove(*obj.tags.filter(category=self))
        obj.tags.add(*tags)

    def __unicode__(self):
        return self.label


class Tag(models.Model):
    label = models.CharField(max_length=64, verbose_name=_('tag'))
    dc_value = models.CharField(max_length=32)
    category = models.ForeignKey(Category)
    help_text = models.CharField(max_length=250, blank=True)
    index = models.IntegerField()

    class Meta:
        ordering = ['index', 'label']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return self.label
