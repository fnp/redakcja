from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from toolbar import models

#class ButtonGroupAdmin(admin.ModelAdmin):
#    list_display = ('name', 'slug', 'position',)
#    search_fields = ('name', 'slug',)
#    prepopulated_fields = {'slug': ('name',)}
#    list_editable = ('position',)
admin.site.register(models.ButtonGroup)

#class ButtonAdmin(admin.ModelAdmin):
#    list_display = ('label', 'action', 'key', 'position',)
#    list_filter = ('group',)
#    search_fields = ('label', 'action', 'key',)
#    filter_horizontal = ('group',)
#    list_editable = ('position',)

admin.site.register(models.Button)
