# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ButtonGroup(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField()
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ('position', 'name',)
        verbose_name, verbose_name_plural = _('button group'), _('button groups')

    def __str__(self):
        return self.name

    def to_dict(self, with_buttons=False):
        d = {'name': self.name, 'position': self.position}

        if with_buttons:
            d['buttons'] = [b.to_dict() for b in self.button_set.all()]

        return d


class Button(models.Model):
    label = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)  # unused

    # behaviour
    params = models.TextField(default='[]')  # TODO: should be a JSON field
    scriptlet = models.ForeignKey('Scriptlet', null=True, blank=True)
    link = models.CharField(max_length=256, blank=True, default='')

    # ui related stuff
    accesskey = models.CharField(blank=True, max_length=1)

    tooltip = models.CharField(blank=True, max_length=120)

    # Why the button is restricted to have the same position in each group ?
    # position = models.IntegerField(default=0)
    group = models.ManyToManyField(ButtonGroup)

    class Meta:
        ordering = ('slug',)
        verbose_name, verbose_name_plural = _('button'), _('buttons')

    @property
    def full_tooltip(self):
        return u"%s %s" % (self.tooltip, "[Alt+%s]" % self.accesskey if self.accesskey else "")

    def to_dict(self):
        return {
            'label': self.label,
            'tooltip': self.tooltip,
            'accesskey': self.accesskey,
            'params': self.params,
            'scriptlet_id': self.scriptlet_id,
        }

    def __str__(self):
        return self.label


class Scriptlet(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    code = models.TextField()

    def __str__(self):
        return _(u'javascript') + u':' + self.name
