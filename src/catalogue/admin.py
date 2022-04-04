# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from admin_numeric_filter.admin import RangeNumericFilter, NumericFilterModelAdmin
from fnpdjango.actions import export_as_csv_action
from . import models
import documents.models
from .wikidata import WikidataAdminMixin


class AuthorAdmin(WikidataAdminMixin, admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "status",
        "year_of_death",
        "gender",
        "nationality",
        "priority",
        "wikidata_link",
        "slug",
    ]
    list_filter = ["year_of_death", "priority", "collections", "status", "gender", "nationality"]
    search_fields = ["first_name", "last_name", "wikidata"]
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    autocomplete_fields = ["collections"]


admin.site.register(models.Author, AuthorAdmin)


class LicenseFilter(admin.SimpleListFilter):
    title = 'Licencja'
    parameter_name = 'book_license'
    license_url_field = 'document_book__dc__license'
    license_name_field = 'document_book__dc__license_description'

    def lookups(self, requesrt, model_admin):
        return [
            ('cc', 'CC'),
            ('fal', 'FAL'),
            ('pd', 'domena publiczna'),
        ]

    def queryset(self, request, queryset):
        v = self.value()
        if v == 'cc': 
            return queryset.filter(**{
                self.license_url_field + '__icontains': 'creativecommons.org'
            })
        elif v == 'fal':
            return queryset.filter(**{
                self.license_url_field + '__icontains': 'artlibre.org'
            })
        elif v == 'pd':
            return queryset.filter(**{
                self.license_name_field + '__icontains': 'domena publiczna'
            })
        else:
            return queryset


class CoverLicenseFilter(LicenseFilter):
    title = 'Licencja okładki'
    parameter_name = 'cover_license'
    license_url_field = 'document_book__dc_cover_image__license_url'
    license_name_field = 'document_book__dc_cover_image__license_name'


class BookAdmin(WikidataAdminMixin, NumericFilterModelAdmin):
    list_display = [
        "smart_title",
        "authors_str",
        "translators_str",
        "language",
        "pd_year",
        "priority",
        "wikidata_link",
    ]
    search_fields = [
        "title", "wikidata",
        "authors__first_name", "authors__last_name",
        "translators__first_name", "translators__last_name",
        "scans_source", "text_source", "notes", "estimate_source",
    ]
    autocomplete_fields = ["authors", "translators", "based_on", "collections", "epochs", "genres", "kinds"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = [
        "language",
        "based_on__language",
        ("pd_year", RangeNumericFilter),
        "collections",
        "collections__category",
        "epochs", "kinds", "genres",
        "priority",
        "authors__gender", "authors__nationality",
        "translators__gender", "translators__nationality",
        "document_book__chunk__stage",
        "document_book__chunk__user",

        LicenseFilter,
        CoverLicenseFilter,
    ]
    readonly_fields = ["wikidata_link", "estimated_costs", "documents_book_link"]
    actions = [export_as_csv_action()]
    fieldsets = [
        (None, {"fields": [("wikidata", "wikidata_link")]}),
        (
            _("Identification"),
            {
                "fields": [
                    "title",
                    ("slug", 'documents_book_link'),
                    "authors",
                    "translators",
                    "language",
                    "based_on",
                    "pd_year",
                ]
            },
        ),
        (
            _("Features"),
            {
                "fields": [
                    "epochs",
                    "genres",
                    "kinds",
                ]
            },
        ),
        (
            _("Plan"),
            {
                "fields": [
                    "scans_source",
                    "text_source",
                    "priority",
                    "collections",
                    "notes",
                    ("estimated_chars", "estimated_verses", "estimate_source"),
                    "estimated_costs",
                ]
            },
        ),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.view_name.endswith("changelist"):
            qs = qs.prefetch_related("authors", "translators")
        return qs

    def estimated_costs(self, obj):
        return "\n".join(
            "{}: {} zł".format(
                work_type.name,
                cost or '—'
            )
            for work_type, cost in obj.get_estimated_costs().items()
        )

    def smart_title(self, obj):
        if obj.title:
            return obj.title
        if obj.notes:
            n = obj.notes
            if len(n) > 100:
                n = n[:100] + '…'
            return mark_safe(
                '<em><small>' + escape(n) + '</small></em>'
            )
        return '---'
    smart_title.short_description = _('Title')
    smart_title.admin_order_field = 'title'

    def documents_book_link(self, obj):
        for book in obj.document_books.all():
            return mark_safe('<a style="position: absolute" href="{}"><img height="100" width="70" src="/cover/preview/{}/?height=100&width=70"></a>'.format(book.get_absolute_url(), book.slug))
    documents_book_link.short_description = _('Book')


admin.site.register(models.Book, BookAdmin)


admin.site.register(models.CollectionCategory)


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
    fields = ['name', 'slug', 'category', 'notes', 'estimated_costs']
    readonly_fields = ['estimated_costs']
    inlines = [AuthorInline, BookInline]

    def estimated_costs(self, obj):
        return "\n".join(
            "{}: {} zł".format(
                work_type.name,
                cost or '—'
            )
            for work_type, cost in obj.get_estimated_costs().items()
        )


admin.site.register(models.Collection, CollectionAdmin)



class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]

admin.site.register(models.Epoch, CategoryAdmin)
admin.site.register(models.Genre, CategoryAdmin)
admin.site.register(models.Kind, CategoryAdmin)



class WorkRateInline(admin.TabularInline):
    model = models.WorkRate
    autocomplete_fields = ['kinds', 'genres', 'epochs', 'collections']


class WorkTypeAdmin(admin.ModelAdmin):
    inlines = [WorkRateInline]

admin.site.register(models.WorkType, WorkTypeAdmin)

