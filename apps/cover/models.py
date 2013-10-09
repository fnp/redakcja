# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from urlparse import urljoin
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from cover.utils import URLOpener


class Image(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    author = models.CharField(max_length=255, verbose_name=_('author'))
    license_name = models.CharField(max_length=255, verbose_name=_('license name'))
    license_url = models.URLField(max_length=255, blank=True, verbose_name=_('license URL'))
    source_url = models.URLField(verbose_name=_('source URL'))
    download_url = models.URLField(unique=True, verbose_name=_('image download URL'), null = True)
    file = models.ImageField(upload_to='cover/image', editable=True, verbose_name=_('file'))

    class Meta:
        verbose_name = _('cover image')
        verbose_name_plural = _('cover images')

    def __unicode__(self):
        return u"%s - %s" % (self.author, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('cover_image', [self.id])

    def get_full_url(self):
        return "http://%s%s" % (Site.objects.get_current().domain, self.get_absolute_url())


@receiver(post_save, sender=Image)
def download_image(sender, instance, **kwargs):
    if instance.pk and not instance.file:
        t = URLOpener().open(instance.download_url).read()
        instance.file.save("%d.jpg" % instance.pk, ContentFile(t))
        
        