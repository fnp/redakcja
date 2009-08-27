import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class PanelSettings(models.Model):
    user = models.ForeignKey(User)
    left_panel = models.CharField(blank=True,  max_length=80)
    right_panel = models.CharField(blank=True,  max_length=80)

    class Meta:
        ordering = ['user__name']
        verbose_name, verbose_name_plural = _("panel settings"), _("panel settings")

    def __unicode__(self):
        return u"Panel settings for %s" % self.user.name


def get_image_folders():
    return sorted(fn for fn in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR)) if not fn.startswith('.'))


def get_images_from_folder(folder):
    return sorted(settings.MEDIA_URL + settings.IMAGE_DIR + '/' + folder + '/' + fn for fn 
            in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, folder))
            if not fn.startswith('.'))

