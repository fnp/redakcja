from django.contrib import admin

import explorer.models
from explorer import forms

admin.site.register(explorer.models.EditorSettings)
admin.site.register(explorer.models.EditorPanel)

class GalleryAdmin(admin.ModelAdmin):
    form = forms.GalleryChoiceForm
    list_display = ('document', 'subpath',)
    search_fields = ('document', 'subpath',)

admin.site.register(explorer.models.GalleryForDocument, GalleryAdmin)