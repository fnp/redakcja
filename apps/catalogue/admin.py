from django.contrib import admin

from catalogue import models

class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Chunk)

admin.site.register(models.Chunk.tag_model)
