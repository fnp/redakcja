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
            {'name': 'htmleditor',
            'ratio': 0.5},
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
  

# Yes, this is intentionally unnormalized !
class GalleryForDocument(models.Model):
    name = models.CharField(max_length=100, blank=True)

    # document associated with the gallery
    document = models.CharField(max_length=255, unique=True)
        
    # directory containing scans under MEDIA_ROOT/
    subpath = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s:%s" % (self.subpath, self.document)

