from django.contrib import admin

from catalogue import models

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'public', '_published', '_new_publishable']
    list_filter = ['public', '_published', '_new_publishable']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title']


admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Chunk)

admin.site.register(models.Chunk.tag_model)
