# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from admin_numeric_filter.admin import RangeNumericFilter, NumericFilterModelAdmin
from admin_ordering.admin import OrderableAdmin
from fnpdjango.actions import export_as_csv_action
from modeltranslation.admin import TabbedTranslationAdmin
from . import models
import documents.models
from .wikidata import WikidataAdminMixin


class NotableBookInline(OrderableAdmin, admin.TabularInline):
    model = models.NotableBook
    autocomplete_fields = ['book']
    ordering_field_hide_input = True


class AuthorAdmin(WikidataAdminMixin, TabbedTranslationAdmin):
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
    list_display_links = [
        "first_name", "last_name"
    ]
    list_filter = [
        ("year_of_death", RangeNumericFilter),
        "priority",
        "collections",
        "status",
        "gender",
        "nationality",
        ("genitive", admin.EmptyFieldListFilter)
    ]
    list_per_page = 10000000
    search_fields = ["first_name", "last_name", "wikidata"]
    readonly_fields = ["wikidata_link", "description_preview"]

    fieldsets = [
        (None, {"fields": [("wikidata", "wikidata_link")]}),
        (
            _("Identification"),
            {
                "fields": [
                    ("first_name", "last_name"),
                    "slug",
                    "gender",
                    "nationality",
                    ("date_of_birth", "year_of_birth", "year_of_birth_inexact", "year_of_birth_range", "place_of_birth"),
                    ("date_of_death", "year_of_death", "year_of_death_inexact", "year_of_death_range", "place_of_death"),
                    ("description", "description_preview"),
                    "status",
                    "collections",
                    "priority",
                    
                    "notes",
                    "gazeta_link",
                    "culturepl_link",
                    "plwiki",
                    "photo", "photo_source", "photo_attribution",
                ]
            },
        ),
    ]
    
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    autocomplete_fields = ["collections", "place_of_birth", "place_of_death"]
    inlines = [
        NotableBookInline,
    ]

    def description_preview(self, obj):
        return obj.generate_description()


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


def add_title(base_class, suffix):
    class TitledCategoryFilter(base_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title += suffix
    return TitledCategoryFilter



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
        ("authors__collections", add_title(admin.RelatedFieldListFilter, ' autora')),
        ("authors__collections__category", add_title(admin.RelatedFieldListFilter, ' autora')),
        ("translators__collections", add_title(admin.RelatedFieldListFilter, ' tłumacza')), 
        ("translators__collections__category", add_title(admin.RelatedFieldListFilter, ' tłumacza')),
        "epochs", "kinds", "genres",
        "priority",
        "authors__gender", "authors__nationality",
        "translators__gender", "translators__nationality",
        "document_book__chunk__stage",

        LicenseFilter,
        CoverLicenseFilter,
        'free_license',
        'polona_missing',
    ]
    list_per_page = 1000000

    readonly_fields = [
        "wikidata_link",
        "estimated_costs",
        "documents_book_link",
        "scans_source_link",
    ]
    actions = [export_as_csv_action(
        fields=[
            "id",
            "wikidata",
            "slug",
            "title",
            "authors_first_names",
            "authors_last_names",
            "translators_first_names",
            "translators_last_names",
            "language",
            "based_on",
            "scans_source",
            "text_source",
            "notes",
            "priority",
            "pd_year",
            "gazeta_link",
            "estimated_chars",
            "estimated_verses",
            "estimate_source"
        ]
    )]
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
                    "original_year",
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
                    ("free_license", "polona_missing"),
                    ("scans_source", "scans_source_link"),
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

    def scans_source_link(self, obj):
        if obj.scans_source:
            return format_html(
                '<a href="{url}" target="_blank">{url}</a>',
                url=obj.scans_source,
            )
        else:
            return ""
    scans_source_link.short_description = _('scans source')


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
    fields = ['name', 'slug', 'category', 'description', 'notes', 'estimated_costs']
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


@admin.register(models.Epoch)
class EpochAdmin(CategoryAdmin):
    list_display = ['name', 'adjective_feminine_singular', 'adjective_nonmasculine_plural']


@admin.register(models.Genre)
class GenreAdmin(CategoryAdmin):
    list_display = ['name', 'plural', 'is_epoch_specific']


@admin.register(models.Kind)
class KindAdmin(CategoryAdmin):
    list_display = ['name', 'collective_noun']



class WorkRateInline(admin.TabularInline):
    model = models.WorkRate
    autocomplete_fields = ['kinds', 'genres', 'epochs', 'collections']


class WorkTypeAdmin(admin.ModelAdmin):
    inlines = [WorkRateInline]

admin.site.register(models.WorkType, WorkTypeAdmin)



@admin.register(models.Place)
class PlaceAdmin(WikidataAdminMixin, TabbedTranslationAdmin):
    search_fields = ['name']
