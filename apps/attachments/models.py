# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Attachment(models.Model):
    key = models.CharField(_('key'), help_text=_('A unique name for this attachment'), primary_key=True, max_length=255)
    attachment = models.FileField(upload_to='attachment')

    class Meta:
        ordering = ('key',)
        verbose_name, verbose_name_plural = _('attachment'), _('attachments')

    def __unicode__(self):
        return self.key
