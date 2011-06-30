from django.contrib import admin

from dvcs import models


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'ordering']

admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Document)
admin.site.register(models.Change)
