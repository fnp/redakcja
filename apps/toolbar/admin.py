from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from toolbar import models


class ButtonGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'position',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('position',)

admin.site.register(models.ButtonGroup, ButtonGroupAdmin)


class ButtonAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'tag', 'key', 'position',)
    list_filter = ('group',)
    search_fields = ('label', 'slug', 'tag', 'key',)
    prepopulated_fields = {'slug': ('label',)}
    filter_horizontal = ('group',)
    list_editable = ('position',)

admin.site.register(models.Button, ButtonAdmin)

