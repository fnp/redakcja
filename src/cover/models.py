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
from librarian.dcparser import BookInfo
from librarian.meta.types.person import Person
from librarian.cover import make_cover
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
        max_length=1024,
        storage=OverwriteStorage(),
        verbose_name=_('file')
    )
    use_file = models.ImageField(
        upload_to='cover/use',
        storage=OverwriteStorage(),
        editable=True,
        verbose_name=_('file for use')
    )

    example = models.ImageField(
        upload_to='cover/example',
        storage=OverwriteStorage(),
        editable=False,
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

        super().save(update_fields=['use_file'])

        self.example.save(
            "%d.jpg" % self.pk,
            ContentFile(self.build_example().get_bytes()),
            save=False
        )
        super().save(update_fields=['example'])
        

    def build_example(self):
        class A:
            pass
        info = A()
        info.authors = []
        info.translators = []
        info.cover_class = None
        info.cover_box_position = None
        info.title = '?'
        info.cover_url = 'file://' + self.use_file.path
        return make_cover(info, width=200).output_file()
    
    def get_absolute_url(self):
        return reverse('cover_image', args=[self.id])

    def get_full_url(self):
        return "http://%s%s" % (Site.objects.get_current().domain, self.get_absolute_url())

    def cut_percentages(self):
        img = PILImage.open(self.file)
        max_w, max_h = 600, 600
        w, h = img.size
        scale = min(max_w / w, max_h / h)
        ws, hs = round(w * scale), round(h * scale)

        return {
            'left': 100 * self.cut_left / w,
            'right': 100 * self.cut_right / w,
            'top': 100 * self.cut_top / h,
            'bottom': 100 * self.cut_bottom / h,
            'width': ws,
            'height': hs,
            'th': f'{ws}x{hs}',
        }

    @property
    def etag(self):
        return f'{self.cut_top}.{self.cut_bottom}.{self.cut_left}.{self.cut_right}'

    @property
    def attribution(self):
        pieces = []
        if self.title:
            pieces.append(self.title)
        if self.author:
            pieces.append(self.author)
        if self.license_name:
            pieces.append(self.license_name)
        if self.source_url:
            pieces.append(self.source_url.split('/')[2])
        return ', '.join(pieces)
    


@receiver(post_save, sender=Image)
def download_image(sender, instance, **kwargs):
    if instance.pk and not instance.file:
        t = URLOpener().open(instance.download_url).read()
        instance.file.save("%d.jpg" % instance.pk, ContentFile(t))
