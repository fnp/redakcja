# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from cover.utils import URLOpener


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class Image(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    author = models.CharField(max_length=255, verbose_name=_('author'))
    license_name = models.CharField(max_length=255, verbose_name=_('license name'))
    license_url = models.URLField(max_length=255, blank=True, verbose_name=_('license URL'))
    source_url = models.URLField(verbose_name=_('source URL'), null=True, blank=True)
    download_url = models.URLField(unique=True, verbose_name=_('image download URL'), null=True, blank=True)
    file = models.ImageField(
        upload_to='cover/image', storage=OverwriteStorage(), editable=True, verbose_name=_('file'))

    class Meta:
        verbose_name = _('cover image')
        verbose_name_plural = _('cover images')

    def __unicode__(self):
        return u"%s - %s" % (self.author, self.title)

    @models.permalink
    def get_absolute_url(self):
        return 'cover_image', [self.id]

    def get_full_url(self):
        return "http://%s%s" % (Site.objects.get_current().domain, self.get_absolute_url())


@receiver(post_save, sender=Image)
def download_image(sender, instance, **kwargs):
    if instance.pk and not instance.file:
        t = URLOpener().open(instance.download_url).read()
        instance.file.save("%d.jpg" % instance.pk, ContentFile(t))
