from django.contrib import admin
from . import models


@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'modified_at', 'processed_at']
    exclude = ['wikisource']

    
@admin.register(models.BookSource)
class BookSourceAdmin(admin.ModelAdmin):
    list_display = ['source', 'page_start', 'page_end', 'book']
    raw_id_fields = ['source', 'book']
