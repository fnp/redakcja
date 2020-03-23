from django.contrib import admin
from . import models



class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(models.Author, AuthorAdmin)


class BookAdmin(admin.ModelAdmin):
    raw_id_fields = ['authors']
    autocomplete_fields = ['translators']

admin.site.register(models.Book, BookAdmin)

