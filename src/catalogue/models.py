from django.db import models
from django.utils.translation import gettext_lazy as _
from .constants import WIKIDATA
from .wikidata import WikidataMixin


class Author(WikidataMixin, models.Model):
    slug = models.SlugField(null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    year_of_death = models.SmallIntegerField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[
            (1, _("Alive")),
            (2, _("Dead")),
            (3, _("Long dead")),
            (4, _("Unknown")),
        ],
    )
    notes = models.TextField(blank=True)
    gazeta_link = models.CharField(max_length=255, blank=True)
    culturepl_link = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(
        default=0, choices=[(0, _("Low")), (1, _("Medium")), (2, _("High"))]
    )

    class Wikidata:
        first_name = WIKIDATA.GIVEN_NAME
        last_name = WIKIDATA.LAST_NAME
        year_of_death = WIKIDATA.DATE_OF_DEATH
        notes = "description"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(WikidataMixin, models.Model):
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    authors = models.ManyToManyField(Author, blank=True)
    translators = models.ManyToManyField(
        Author,
        related_name="translated_book_set",
        related_query_name="translated_book",
        blank=True,
    )
    title = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=3, blank=True)
    based_on = models.ForeignKey(
        "self", models.PROTECT, related_name="translation", null=True, blank=True
    )
    scans_source = models.CharField(max_length=255, blank=True)
    text_source = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(
        default=0, choices=[(0, _("Low")), (1, _("Medium")), (2, _("High"))]
    )
    pd_year = models.IntegerField(null=True, blank=True)

    class Wikidata:
        authors = WIKIDATA.AUTHOR
        translators = WIKIDATA.TRANSLATOR
        title = WIKIDATA.TITLE
        language = WIKIDATA.LANGUAGE
        based_on = WIKIDATA.BASED_ON
        notes = "description"

    def __str__(self):
        return self.title
