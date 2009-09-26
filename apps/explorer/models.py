# -*- encoding: utf-8 -*-
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _

import toolbar.models

from explorer import fields

class EditorSettings(models.Model):
    """Ustawienia edytora dla użytkownika.
    
    Pole settings zawiera obiekt JSON o  kluczach:
     - panels - lista otwartych paneli i ich proporcje
     - recentFiles - lista otwartych plików i ustawienia dla nich
    
    Przykład:
    {
        'panels': [
            {'name': 'htmleditor', 'ratio': 0.5},
            {'name': 'gallery', 'ratio': 0.5}
        ],
        'recentFiles': [
            {
                'fileId': 'mickiewicz_pan_tadeusz.xml',
                'panels': [
                    {'name': 'htmleditor', 'ratio': 0.4},
                    {'name': 'gallery', 'ratio': 0.6}
                ]
            }
        ]
    }
    """
    user = models.ForeignKey(User, unique=True)
    settings = fields.JSONField()
    
    class Meta:
        verbose_name, verbose_name_plural = _("editor settings"), _("editor settings")

    def __unicode__(self):
        return u"Editor settings for %s" % self.user.username

class EditorPanel(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    display_name = models.CharField(max_length=128)

    toolbar_groups = models.ManyToManyField(toolbar.models.ButtonGroup, blank=True)
    toolbar_extra = models.ForeignKey(toolbar.models.ButtonGroup, null=True, blank=True,
        unique=True, related_name='main_editor_panels')

    def __unicode__(self):
        return self.display_name
    
class Book(models.Model):
    class Meta:
        permissions = (            
            ("can_share", "Can share documents without pull requests."),
        )
        abstract=True
    pass


class PullRequest(models.Model):

    REQUEST_STATUSES = (
        ("N", "Pending for resolution"),
        ("R", "Rejected"),
        ("A", "Accepted & merged"),
    )

    comitter = models.ForeignKey(User) # the user who request the pull
    comment = models.TextField() # addtional comments to the request

    # document to merge
    document = models.CharField(max_length=255)

    # revision to be merged into the main branch
    source_revision = models.CharField(max_length=40, unique=True)

    # current status
    status = models.CharField(max_length=1, choices=REQUEST_STATUSES)

    # comment to the status change of request (if applicable)
    response_comment = models.TextField(blank=True)

    # revision number in which the changes were merged (if any)
    merged_rev = models.CharField(max_length=40, blank=True, null=True)


    def __unicode__(self):
        return unicode(self.comitter) + u':' + self.document
    
def get_image_folders():
    return sorted(fn for fn in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR)) if not fn.startswith('.'))


def get_images_from_folder(folder):
    return sorted(settings.MEDIA_URL + settings.IMAGE_DIR + u'/' + folder + u'/' + fn.decode('utf-8') for fn
            in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, folder))
            if not fn.decode('utf-8').startswith('.'))

