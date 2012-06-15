# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from urllib2 import urlopen
from urlparse import urljoin
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class Image(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    license_name = models.CharField(max_length=255)
    license_url = models.URLField(max_length=255, blank=True)
    source_url = models.URLField()
    download_url = models.URLField(unique=True)
    file = models.ImageField(upload_to='cover/image', editable=False)

    class Meta:
        verbose_name = _('cover image')
        verbose_name_plural = _('cover images')

    def __unicode__(self):
        return u"%s - %s" % (self.author, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('cover_image', [self.id])


@receiver(post_save, sender=Image)
def download_image(sender, instance, **kwargs):
    if instance.pk and not instance.file:
        t = urlopen(instance.download_url).read()
        instance.file.save("%d.jpg" % instance.pk, ContentFile(t))
        
        