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


class PullRequest(models.Model):
    comitter = models.ForeignKey(User) # the user who request the pull 
    file = models.CharField(max_length=256) # the file to request
    source_rev = models.CharField(max_length=40) # revision number of the commiter

    comment = models.TextField() # addtional comments to the request

    # revision number in which the changes were merged (if any)
    merged_rev = models.CharField(max_length=40, null=True) 
    
    def __unicode__(self):
        return u"Pull request from %s, source: %s %s, status: %s." % \
            (self.commiter, self.file, self.source_rev, \
                (("merged into "+self.merged_rev) if self.merged_rev else "pending") )

    
def get_image_folders():
    return sorted(fn for fn in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR)) if not fn.startswith('.'))


def get_images_from_folder(folder):
    return sorted(settings.MEDIA_URL + settings.IMAGE_DIR + '/' + folder + '/' + fn for fn 
            in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, folder))
            if not fn.startswith('.'))

def user_branch(user):
    return 'personal_'+user.username
