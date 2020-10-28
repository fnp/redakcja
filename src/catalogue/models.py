import decimal
from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wikidata.client import Client
from .constants import WIKIDATA
from .utils import UnrelatedManager
from .wikidata import WikidataMixin


class Author(WikidataMixin, models.Model):
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    name_de = models.CharField(max_length=255, blank=True)
    name_lt = models.CharField(max_length=255, blank=True)

    gender = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=255, blank=True)
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
    description_de = models.TextField(blank=True)
    description_lt = models.TextField(blank=True)

    priority = models.PositiveSmallIntegerField(
        default=0, choices=[(0, _("Low")), (1, _("Medium")), (2, _("High"))]
    )
    collections = models.ManyToManyField("Collection", blank=True)

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')
        ordering = ("last_name", "first_name", "year_of_death")

    class Wikidata:
        first_name = WIKIDATA.GIVEN_NAME
        last_name = WIKIDATA.LAST_NAME
        year_of_death = WIKIDATA.DATE_OF_DEATH
        gender = WIKIDATA.GENDER
        notes = "description"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("catalogue_author", args=[self.slug])

    @property
    def pd_year(self):
        if self.year_of_death:
            return self.year_of_death + 71
        elif self.year_of_death == 0:
            return 0
        else:
            return None


class Category(WikidataMixin, models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Epoch(Category):
    class Meta:
        verbose_name = _('epoch')
        verbose_name_plural = _('epochs')


class Genre(Category):
    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class Kind(Category):
    class Meta:
        verbose_name = _('kind')
        verbose_name_plural = _('kinds')


class Book(WikidataMixin, models.Model):
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    authors = models.ManyToManyField(Author, blank=True)
    translators = models.ManyToManyField(
        Author,
        related_name="translated_book_set",
        related_query_name="translated_book",
        blank=True,
    )
    epochs = models.ManyToManyField(Epoch, blank=True)
    kinds = models.ManyToManyField(Kind, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    title = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=255, blank=True)
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
    gazeta_link = models.CharField(max_length=255, blank=True)
    collections = models.ManyToManyField("Collection", blank=True)

    estimated_chars = models.IntegerField(null=True, blank=True)
    estimated_verses = models.IntegerField(null=True, blank=True)
    estimate_source = models.CharField(max_length=2048, blank=True)

    objects = UnrelatedManager()

    class Meta:
        ordering = ("title",)
        verbose_name = _('book')
        verbose_name_plural = _('books')

    class Wikidata:
        authors = WIKIDATA.AUTHOR
        translators = WIKIDATA.TRANSLATOR
        title = WIKIDATA.TITLE
        language = WIKIDATA.LANGUAGE
        based_on = WIKIDATA.BASED_ON
        notes = "description"

    def __str__(self):
        txt = self.title
        astr = self.authors_str()
        if astr:
            txt = f"{astr} – {txt}"
        tstr = self.translators_str()
        if tstr:
            txt = f"{txt} (tłum. {tstr})"
        return txt

    def get_absolute_url(self):
        return reverse("catalogue_book", args=[self.slug])
    
    def authors_str(self):
        return ", ".join(str(author) for author in self.authors.all())

    def translators_str(self):
        return ", ".join(str(author) for author in self.translators.all())

    def get_document_books(self):
        DBook = apps.get_model("documents", "Book")
        return DBook.objects.filter(dc_slug=self.slug)

    def get_estimated_costs(self):
        return {
            work_type: work_type.calculate(self)
            for work_type in WorkType.objects.all()
        }


class Collection(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name = _('collection')
        verbose_name_plural = _('collections')

    def __str__(self):
        return self.name


class WorkType(models.Model):
    name = models.CharField(max_length=255)

    def get_rate_for(self, book):
        for workrate in self.workrate_set.all():
            if workrate.matches(book):
                return workrate

    def calculate(self, book):
        workrate = self.get_rate_for(book)
        if workrate is not None:
            return workrate.calculate(book)
        


class WorkRate(models.Model):
    priority = models.IntegerField(default=1)
    per_normpage = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    per_verse = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    work_type = models.ForeignKey(WorkType, models.CASCADE)
    epochs = models.ManyToManyField(Epoch, blank=True)
    kinds = models.ManyToManyField(Kind, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)

    class Meta:
        ordering = ('priority',)

    def matches(self, book):
        for category in 'epochs', 'kinds', 'genres', 'collections':
            oneof = getattr(self, category).all()
            if oneof:
                if not set(oneof).intersection(
                        getattr(book, category).all()):
                    return False
        return True

    def calculate(self, book):
        if self.per_verse:
            if book.estimated_verses:
                return book.estimated_verses * self.per_verse
        elif self.per_normpage:
            if book.estimated_chars:
                return (decimal.Decimal(book.estimated_chars) / 1800 * self.per_normpage).quantize(decimal.Decimal('1.00'), rounding=decimal.ROUND_HALF_UP)

