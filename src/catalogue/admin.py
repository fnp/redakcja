from django.contrib import admin
from . import models
from .wikidata import WikidataAdminMixin


class AuthorAdmin(WikidataAdminMixin, admin.ModelAdmin):
    list_display = "first_name", "last_name", "notes"
    search_fields = ["first_name", "last_name", "wikidata"]
    prepopulated_fields = {"slug": ("first_name", "last_name")}


admin.site.register(models.Author, AuthorAdmin)


class BookAdmin(WikidataAdminMixin, admin.ModelAdmin):
    list_display = "title", "notes"
    autocomplete_fields = ["authors", "translators"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(models.Book, BookAdmin)
