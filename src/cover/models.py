# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site
from PIL import Image as PILImage
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
    download_url = models.URLField(max_length=4096, unique=True, verbose_name=_('image download URL'), null=True, blank=True)
    file = models.ImageField(
        upload_to='cover/image',
        storage=OverwriteStorage(),
        verbose_name=_('file')
    )
    use_file = models.ImageField(
        upload_to='cover/use',
        storage=OverwriteStorage(),
        editable=True,
        verbose_name=_('file for use')
    )
    cut_top = models.IntegerField(default=0, )
    cut_bottom = models.IntegerField(default=0)
    cut_left = models.IntegerField(default=0)
    cut_right = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('cover image')
        verbose_name_plural = _('cover images')

    def __str__(self):
        return u"%s - %s" % (self.author, self.title)

    def save(self, **kwargs):
        super().save(**kwargs)
        img = self.file
        if self.cut_top or self.cut_bottom or self.cut_left or self.cut_right:
            img = PILImage.open(img)
            img = img.crop((
                self.cut_left,
                self.cut_top,
                img.size[0] - self.cut_right,
                img.size[1] - self.cut_bottom,
            ))
            buffer = BytesIO()
            img.save(
                buffer,
                format='JPEG',
            )
            img = ContentFile(buffer.getvalue())
        self.use_file.save(
            "%d.jpg" % self.pk,
            img,
            save=False
        )
        super().save(**kwargs)
    
    def get_absolute_url(self):
        return reverse('cover_image', args=[self.id])

    def get_full_url(self):
        return "http://%s%s" % (Site.objects.get_current().domain, self.get_absolute_url())


@receiver(post_save, sender=Image)
def download_image(sender, instance, **kwargs):
    if instance.pk and not instance.file:
        t = URLOpener().open(instance.download_url).read()
        instance.file.save("%d.jpg" % instance.pk, ContentFile(t))
