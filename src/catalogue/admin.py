# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from django.contrib import admin
from django.db.models import Min
from django import forms
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from admin_numeric_filter.admin import RangeNumericFilter, NumericFilterModelAdmin, RangeNumericForm
from admin_ordering.admin import OrderableAdmin
from fnpdjango.actions import export_as_csv_action
from modeltranslation.admin import TabbedTranslationAdmin
from reversion.admin import VersionAdmin
from . import models
import documents.models
import sources.models
from .wikidata import WikidataAdminMixin


class NotableBookInline(OrderableAdmin, admin.TabularInline):
    model = models.NotableBook
    autocomplete_fields = ['book']
    ordering_field_hide_input = True


class WoblinkCatalogueWidget(forms.Select):
    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/vendor/select2/select2.full.min.js",
            "admin/js/vendor/select2/i18n/pl.js",
            "catalogue/woblink_admin.js",
            "admin/js/jquery.init.js",
            "admin/js/autocomplete.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.min.css",
                "admin/css/autocomplete.css",
            ),
        }

    def __init__(self):
        self.attrs = {}
        self.choices = []
        self.field = None

    def get_url(self):
        return reverse('catalogue_woblink_autocomplete', args=[self.category])

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault("class", "")
        attrs.update(
            {
                "data-ajax--cache": "true",
                "data-ajax--delay": 250,
                "data-ajax--type": "GET",
                "data-ajax--url": self.get_url(),
                "data-app-label": '',
                "data-model-name": '',
                "data-field-name": '',
                "data-theme": "admin-autocomplete",
                "data-allow-clear": json.dumps(not self.is_required),

                "data-placeholder": "", # Chyba że znaleziony?
                "lang": "pl",
                "class": attrs["class"]
                + (" " if attrs["class"] else "")
                + "admin-autocomplete admin-woblink",
            }
        )
        return attrs

    def optgroups(self, name, value, attrs=None):
        """ Add synthetic option for keeping the current value. """
        return [(None, [
            self.create_option(
                name,
                v,
                '(bez zmian)',
                selected=True,
                index=index,
                attrs=attrs,
            )
            for index, v in enumerate(value)
        ], 0)]

class WoblinkAuthorWidget(WoblinkCatalogueWidget):
    category = 'author'

class AuthorForm(forms.ModelForm):
    class Meta:
        model = models.Author
        fields = '__all__'
        widgets = {
            'woblink': WoblinkAuthorWidget,
        }

class AuthorAdmin(WikidataAdminMixin, TabbedTranslationAdmin, VersionAdmin):
    form = AuthorForm
    list_display = [
        "first_name",
        "last_name",
        "status",
        "year_of_death",
        "gender",
        "nationality",
        "priority",
        "wikidata_link",
        "woblink_link",
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
        "place_of_birth",
        "place_of_death",
        ("genitive", admin.EmptyFieldListFilter)
    ]
    list_per_page = 10000000
    search_fields = ["first_name", "last_name", "wikidata"]
    readonly_fields = ["wikidata_link", "description_preview", "woblink_link"]
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    autocomplete_fields = ["collections", "place_of_birth", "place_of_death"]
    inlines = [
        NotableBookInline,
    ]

    fieldsets = [
        (None, {
            "fields": [
                ("wikidata", "wikidata_link"),
                ("woblink", "woblink_link"),
            ]
        }),
        (
            _("Identification"),
            {
                "fields": [
                    ("first_name", "last_name"),
                    "slug",
                    "genitive",
                    "gender",
                    "nationality",
                    (
                        "date_of_birth",
                        "year_of_birth",
                        "year_of_birth_inexact",
                        "year_of_birth_range",
                        "century_of_birth",
                        "place_of_birth"
                    ),
                    (
                        "date_of_death",
                        "year_of_death",
                        "year_of_death_inexact",
                        "year_of_death_range",
                        "century_of_death",
                        "place_of_death"
                    ),
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

    def description_preview(self, obj):
        return obj.generate_description()

    def woblink_link(self, obj):
        if obj.woblink:
            return format_html(
                '<a href="https://woblink.com/autor/{slug}-{w}" target="_blank">{w}</a>',
                w=obj.woblink,
                slug=obj.slug,
            )
        else:
            return ""
    woblink_link.admin_order_field = "woblink"


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


class FirstPublicationYearFilter(admin.ListFilter):
    title = 'Rok pierwszej publikacji'
    parameter_name = 'first_publication_year'
    template = 'admin/filter_numeric_range.html'

    def __init__(self, request, params, *args, **kwargs):
        super().__init__(request, params, *args, **kwargs)

        self.request = request

        if self.parameter_name + '_from' in params:
            value = params.pop(self.parameter_name + '_from')
            self.used_parameters[self.parameter_name + '_from'] = value

        if self.parameter_name + '_to' in params:
            value = params.pop(self.parameter_name + '_to')
            self.used_parameters[self.parameter_name + '_to'] = value

    def has_output(self):
        return True

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + '_from', None)
        if value_from is not None and value_from != '':
            filters.update({
                self.parameter_name + '__gte': self.used_parameters.get(self.parameter_name + '_from', None),
            })

        value_to = self.used_parameters.get(self.parameter_name + '_to', None)
        if value_to is not None and value_to != '':
            filters.update({
                self.parameter_name + '__lte': self.used_parameters.get(self.parameter_name + '_to', None),
            })

        return queryset.filter(**filters)

    def choices(self, changelist):
        return ({
            'request': self.request,
            'parameter_name': self.parameter_name,
            'form': RangeNumericForm(name=self.parameter_name, data={
                self.parameter_name + '_from': self.used_parameters.get(self.parameter_name + '_from', None),
                self.parameter_name + '_to': self.used_parameters.get(self.parameter_name + '_to', None),
            }),
        }, )

    def expected_parameters(self):
        return [
            '{}_from'.format(self.parameter_name),
            '{}_to'.format(self.parameter_name),
        ]


class SourcesInline(admin.TabularInline):
    model = sources.models.BookSource
    extra = 1


class BookAdmin(WikidataAdminMixin, NumericFilterModelAdmin, VersionAdmin):
    inlines = [SourcesInline]
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
    autocomplete_fields = ["authors", "translators", "based_on", "epochs", "genres", "kinds"]
    filter_horizontal = ['collections']
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

        ("authors__place_of_birth", add_title(admin.RelatedFieldListFilter, ' autora')),
        ("authors__place_of_death", add_title(admin.RelatedFieldListFilter, ' autora')),
        ("translators__place_of_birth", add_title(admin.RelatedFieldListFilter, ' tłumacza')),
        ("translators__place_of_death", add_title(admin.RelatedFieldListFilter, ' tłumacza')),

        "document_book__chunk__stage",

        LicenseFilter,
        CoverLicenseFilter,
        'free_license',
        'polona_missing',

        FirstPublicationYearFilter,
    ]
    list_per_page = 1000000

    readonly_fields = [
        "wikidata_link",
        "estimated_costs",
        "documents_book_link",
        "scans_source_link",
        "monthly_views_page",
        "monthly_views_reader",
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
            "estimate_source",

            "document_book__project",
            "audience",
            "first_publication_year",

            "monthly_views_page",
            "monthly_views_reader",

            # content stats
            "chars",
            "chars_with_fn",
            "words",
            "words_with_fn",
            "verses",
            "chars_out_verse",
            "verses_with_fn",
            "chars_out_verse_with_fn",
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
                    "plwiki",
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
                    ("monthly_views_page", "monthly_views_reader"),
                ]
            },
        ),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.view_name.endswith("changelist"):
            qs = qs.prefetch_related("authors", "translators")
            qs = qs.annotate(first_publication_year=Min('document_book__publish_log__timestamp__year'))
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


admin.site.register(models.CollectionCategory, VersionAdmin)


class AuthorInline(admin.TabularInline):
    model = models.Author.collections.through
    autocomplete_fields = ["author"]


class BookInline(admin.TabularInline):
    model = models.Book.collections.through
    autocomplete_fields = ["book"]


class CollectionAdmin(VersionAdmin):
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



class CategoryAdmin(VersionAdmin):
    search_fields = ["name"]

    def has_description(self, obj):
        return bool(obj.description)
    has_description.boolean = True
    has_description.short_description = 'opis'


@admin.register(models.Epoch)
class EpochAdmin(CategoryAdmin):
    list_display = [
        'name',
        'adjective_feminine_singular',
        'adjective_nonmasculine_plural',
        'has_description',
    ]


@admin.register(models.Genre)
class GenreAdmin(CategoryAdmin):
    list_display = [
        'name',
        'plural',
        'is_epoch_specific',
        'has_description',
    ]


@admin.register(models.Kind)
class KindAdmin(CategoryAdmin):
    list_display = [
        'name',
        'collective_noun',
        'has_description',
    ]



class WorkRateInline(admin.TabularInline):
    model = models.WorkRate
    autocomplete_fields = ['kinds', 'genres', 'epochs', 'collections']


class WorkTypeAdmin(VersionAdmin):
    inlines = [WorkRateInline]

admin.site.register(models.WorkType, WorkTypeAdmin)



@admin.register(models.Place)
class PlaceAdmin(WikidataAdminMixin, TabbedTranslationAdmin, VersionAdmin):
    search_fields = ['name']


@admin.register(models.Thema)
class ThemaAdmin(VersionAdmin):
    list_display = ['code', 'name', 'usable', 'hidden', 'woblink_category']
    list_filter = ['usable', 'usable_as_main', 'hidden']
    search_fields = ['code', 'name', 'description', 'public_description']
    prepopulated_fields = {"slug": ["name"]}



class WoblinkSeriesWidget(WoblinkCatalogueWidget):
    category = 'series'

class AudienceForm(forms.ModelForm):
    class Meta:
        model = models.Audience
        fields = '__all__'
        widgets = {
            'woblink': WoblinkSeriesWidget,
        }

@admin.register(models.Audience)
class AudienceAdmin(VersionAdmin):
    form = AudienceForm
    list_display = ['code', 'name', 'thema', 'woblink']
    search_fields = ['code', 'name', 'description', 'thema', 'woblink']
    prepopulated_fields = {"slug": ["name"]}
    fields = ['code', 'name', 'slug', 'description', 'thema', ('woblink', 'woblink_id')]
    readonly_fields = ['woblink_id']

    def woblink_id(self, obj):
        return obj.woblink or ''
