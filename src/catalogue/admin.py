from django.contrib import admin
from . import models
from .wikidata import WikidataAdminMixin


class AuthorAdmin(WikidataAdminMixin, admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "status",
        "year_of_death",
        "priority",
        "wikidata_link",
        "slug",
    ]
    list_filter = ["year_of_death", "priority", "collections", "status"]
    search_fields = ["first_name", "last_name", "wikidata"]
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    autocomplete_fields = ["collections"]


admin.site.register(models.Author, AuthorAdmin)


class BookAdmin(WikidataAdminMixin, admin.ModelAdmin):
    list_display = [
        "title",
        "authors_str",
        "translators_str",
        "language",
        "pd_year",
        "priority",
        "wikidata_link",
    ]
    search_fields = ["title", "wikidata"]
    autocomplete_fields = ["authors", "translators", "based_on", "collections"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ["language", "pd_year", "collections"]
    readonly_fields = ["wikidata_link"]
    fieldsets = [
        (None, {"fields": [("wikidata", "wikidata_link")]}),
        (
            "Identification",
            {
                "fields": [
                    "title",
                    "slug",
                    "authors",
                    "translators",
                    "language",
                    "based_on",
                    "pd_year",
                ]
            },
        ),
        (
            "Plan",
            {
                "fields": [
                    "scans_source",
                    "text_source",
                    "priority",
                    "collections",
                    "notes",
                ]
            },
        ),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.view_name.endswith("changelist"):
            qs = qs.prefetch_related("authors", "translators")
        return qs


admin.site.register(models.Book, BookAdmin)


class AuthorInline(admin.TabularInline):
    model = models.Author.collections.through
    autocomplete_fields = ["author"]


class BookInline(admin.TabularInline):
    model = models.Book.collections.through
    autocomplete_fields = ["book"]


class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name"]
    autocomplete_fields = []
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    inlines = [AuthorInline, BookInline]


admin.site.register(models.Collection, CollectionAdmin)
