# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from . import models

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'public', '_published', '_new_publishable', 'project']
    list_filter = ['public', '_published', '_new_publishable', 'project']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title']


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'ordering']
    list_editable = ['ordering']

admin.site.register(models.Project)
admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Chunk)
admin.site.register(models.Chunk.tag_model, TagAdmin)

admin.site.register(models.Image)
admin.site.register(models.Image.tag_model, TagAdmin)
