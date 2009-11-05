from django.contrib import admin
from django import forms
import os

from django.conf import settings

import explorer.models

admin.site.register(explorer.models.EditorSettings)
admin.site.register(explorer.models.EditorPanel)


class GalleryAdminForm(forms.ModelForm):
    subpath = forms.ChoiceField(choices=())
    
    def __init__(self, *args, **kwargs):
        super(GalleryAdminForm, self).__init__(*args, **kwargs)
        self.fields['subpath'].choices = [(x, x) for x in os.listdir(settings.MEDIA_ROOT + settings.IMAGE_DIR)]
        
    class Meta:
        mode = explorer.models.GalleryForDocument
        fields = ('document', 'subpath',)


class GalleryAdmin(admin.ModelAdmin):
    form = GalleryAdminForm
    list_display = ('document', 'subpath',)
    search_fields = ('document', 'subpath',)

admin.site.register(explorer.models.GalleryForDocument, GalleryAdmin)