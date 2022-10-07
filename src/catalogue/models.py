from collections import Counter
import decimal
from django.apps import apps
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from admin_ordering.models import OrderableModel
from wikidata.client import Client
from .constants import WIKIDATA
from .wikidata import WikidataModel
from .wikimedia import WikiMedia


class Author(WikidataModel):
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    first_name = models.CharField(_("first name"), max_length=255, blank=True)
    last_name = models.CharField(_("last name"), max_length=255, blank=True)

    name_de = models.CharField(_("name (de)"), max_length=255, blank=True)
    name_lt = models.CharField(_("name (lt)"), max_length=255, blank=True)

    gender = models.CharField(_("gender"), max_length=255, blank=True)
    nationality = models.CharField(_("nationality"), max_length=255, blank=True)
    year_of_birth = models.SmallIntegerField(_("year of birth"), null=True, blank=True)
    year_of_birth_inexact = models.BooleanField(_("inexact"), default=False)
    year_of_birth_range = models.SmallIntegerField(_("year of birth, range end"), null=True, blank=True)
    date_of_birth = models.DateField(_("date_of_birth"), null=True, blank=True)
    place_of_birth = models.ForeignKey(
        'Place', models.PROTECT, null=True, blank=True,
        verbose_name=_('place of birth'),
        related_name='authors_born'
    )
    year_of_death = models.SmallIntegerField(_("year of death"), null=True, blank=True)
    year_of_death_inexact = models.BooleanField(_("inexact"), default=False)
    year_of_death_range = models.SmallIntegerField(_("year of death, range end"), null=True, blank=True)
    date_of_death = models.DateField(_("date_of_death"), null=True, blank=True)
    place_of_death = models.ForeignKey(
        'Place', models.PROTECT, null=True, blank=True,
        verbose_name=_('place of death'),
        related_name='authors_died'
    )
    status = models.PositiveSmallIntegerField(
        _("status"), 
        null=True,
        blank=True,
        choices=[
            (1, _("Alive")),
            (2, _("Dead")),
            (3, _("Long dead")),
            (4, _("Unknown")),
        ],
    )
    notes = models.TextField(_("notes"), blank=True)

    gazeta_link = models.CharField(_("gazeta link"), max_length=255, blank=True)
    culturepl_link = models.CharField(_("culture.pl link"), max_length=255, blank=True)
    plwiki = models.CharField(blank=True, max_length=255)
    photo = models.ImageField(blank=True, null=True, upload_to='catalogue/author/')
    photo_source = models.CharField(blank=True, max_length=255)
    photo_attribution = models.CharField(max_length=255, blank=True)

    description = models.TextField(_("description"), blank=True)

    priority = models.PositiveSmallIntegerField(
        _("priority"), 
        default=0, choices=[(0, _("Low")), (1, _("Medium")), (2, _("High"))]
    )
    collections = models.ManyToManyField("Collection", blank=True, verbose_name=_("collections"))

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')
        ordering = ("last_name", "first_name", "year_of_death")

    class Wikidata:
        first_name = WIKIDATA.GIVEN_NAME
        last_name = WIKIDATA.LAST_NAME
        date_of_birth = WIKIDATA.DATE_OF_BIRTH
        year_of_birth = WIKIDATA.DATE_OF_BIRTH
        place_of_birth = WIKIDATA.PLACE_OF_BIRTH
        date_of_death = WIKIDATA.DATE_OF_DEATH
        year_of_death = WIKIDATA.DATE_OF_DEATH
        place_of_death = WIKIDATA.PLACE_OF_DEATH
        gender = WIKIDATA.GENDER
        notes = "description"
        plwiki = "plwiki"
        photo = WikiMedia.download(WIKIDATA.IMAGE)
        photo_source = WikiMedia.descriptionurl(WIKIDATA.IMAGE)
        photo_attribution = WikiMedia.attribution(WIKIDATA.IMAGE)

        def _supplement(obj):
            if not obj.first_name and not obj.last_name:
                yield 'first_name', 'label'

    def __str__(self):
        name = f"{self.first_name} {self.last_name}"
        if self.year_of_death is not None:
            name += f' (zm. {self.year_of_death})'
        return name

    def get_absolute_url(self):
        return reverse("catalogue_author", args=[self.slug])

    @property
    def name(self):
        return f"{self.last_name}, {self.first_name}"
    
    @property
    def pd_year(self):
        if self.year_of_death:
            return self.year_of_death + 71
        elif self.year_of_death == 0:
            return 0
        else:
            return None

    def generate_description(self):
        t = render_to_string(
            'catalogue/author_description.html',
            {'obj': self}
        )
        return t

class NotableBook(OrderableModel):
    author = models.ForeignKey(Author, models.CASCADE)
    book = models.ForeignKey('Book', models.CASCADE)


class Category(WikidataModel):
    name = models.CharField(_("name"), max_length=255)
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


class Book(WikidataModel):
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    authors = models.ManyToManyField(Author, blank=True, verbose_name=_("authors"))
    translators = models.ManyToManyField(
        Author,
        related_name="translated_book_set",
        related_query_name="translated_book",
        blank=True,
        verbose_name=_("translators")
    )
    epochs = models.ManyToManyField(Epoch, blank=True, verbose_name=_("epochs"))
    kinds = models.ManyToManyField(Kind, blank=True, verbose_name=_("kinds"))
    genres = models.ManyToManyField(Genre, blank=True, verbose_name=_("genres"))
    title = models.CharField(_("title"), max_length=255, blank=True)
    language = models.CharField(_("language"), max_length=255, blank=True)
    based_on = models.ForeignKey(
        "self", models.PROTECT, related_name="translation", null=True, blank=True,
        verbose_name=_("based on")
    )
    scans_source = models.CharField(_("scans source"), max_length=255, blank=True)
    text_source = models.CharField(_("text source"), max_length=255, blank=True)
    notes = models.TextField(_("notes"), blank=True)
    priority = models.PositiveSmallIntegerField(
        _("priority"),
        default=0, choices=[(0, _("Low")), (1, _("Medium")), (2, _("High"))]
    )
    original_year = models.IntegerField(_('original publication year'), null=True, blank=True)
    pd_year = models.IntegerField(_('year of entry into PD'), null=True, blank=True)
    gazeta_link = models.CharField(_("gazeta link"), max_length=255, blank=True)
    collections = models.ManyToManyField("Collection", blank=True, verbose_name=_("collections"))

    estimated_chars = models.IntegerField(_("estimated number of characters"), null=True, blank=True)
    estimated_verses = models.IntegerField(_("estimated number of verses"), null=True, blank=True)
    estimate_source = models.CharField(_("source of estimates"), max_length=2048, blank=True)

    free_license = models.BooleanField(_('free license'), default=False)
    polona_missing = models.BooleanField(_('missing on Polona'), default=False)

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
        original_year = WIKIDATA.PUBLICATION_DATE
        notes = "description"

    def __str__(self):
        txt = self.title
        if self.original_year:
            txt = f"{txt} ({self.original_year})"
        astr = self.authors_str()
        if astr:
            txt = f"{txt}, {astr}"
        tstr = self.translators_str()
        if tstr:
            txt = f"{txt}, tłum. {tstr}"
        return txt

    def get_absolute_url(self):
        return reverse("catalogue_book", args=[self.slug])

    @property
    def wluri(self):
        return f'https://wolnelektury.pl/katalog/lektura/{self.slug}/'
    
    def authors_str(self):
        return ", ".join(str(author) for author in self.authors.all())
    authors_str.admin_order_field = 'authors__last_name'
    authors_str.short_description = _('Author')

    def translators_str(self):
        return ", ".join(str(author) for author in self.translators.all())
    translators_str.admin_order_field = 'translators__last_name'
    translators_str.short_description = _('Translator')

    def get_estimated_costs(self):
        return {
            work_type: work_type.calculate(self)
            for work_type in WorkType.objects.all()
        }


class CollectionCategory(models.Model):
    name = models.CharField(_("name"), max_length=255)
    parent = models.ForeignKey('self', models.SET_NULL, related_name='children', null=True, blank=True, verbose_name=_("parent"))
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        ordering = ('parent__name', 'name')
        verbose_name = _('collection category')
        verbose_name_plural = _('collection categories')

    def __str__(self):
        if self.parent:
            return f"{self.parent} / {self.name}"
        else:
            return self.name


class Collection(models.Model):
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(CollectionCategory, models.SET_NULL, null=True, blank=True, verbose_name=_("category"))
    notes = models.TextField(_("notes"), blank=True)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        ordering = ('category', 'name')
        verbose_name = _('collection')
        verbose_name_plural = _('collections')

    def __str__(self):
        if self.category:
            return f"{self.category} / {self.name}"
        else:
            return self.name

    def get_estimated_costs(self):
        costs = Counter()
        for book in self.book_set.all():
            for k, v in book.get_estimated_costs().items():
                costs[k] += v or 0

        for author in self.author_set.all():
            for book in author.book_set.all():
                for k, v in book.get_estimated_costs().items():
                    costs[k] += v or 0
            for book in author.translated_book_set.all():
                for k, v in book.get_estimated_costs().items():
                    costs[k] += v or 0
        return costs


class WorkType(models.Model):
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name = _('work type')
        verbose_name_plural = _('work types')
    
    def get_rate_for(self, book):
        for workrate in self.workrate_set.all():
            if workrate.matches(book):
                return workrate

    def calculate(self, book):
        workrate = self.get_rate_for(book)
        if workrate is not None:
            return workrate.calculate(book)
        


class WorkRate(models.Model):
    priority = models.IntegerField(_("priority"), default=1)
    per_normpage = models.DecimalField(_("per normalized page"), decimal_places=2, max_digits=6, null=True, blank=True)
    per_verse = models.DecimalField(_("per verse"), decimal_places=2, max_digits=6, null=True, blank=True)
    work_type = models.ForeignKey(WorkType, models.CASCADE, verbose_name=_("work type"))
    epochs = models.ManyToManyField(Epoch, blank=True, verbose_name=_("epochs"))
    kinds = models.ManyToManyField(Kind, blank=True, verbose_name=_("kinds"))
    genres = models.ManyToManyField(Genre, blank=True, verbose_name=_("genres"))
    collections = models.ManyToManyField(Collection, blank=True, verbose_name=_("collections"))

    class Meta:
        ordering = ('priority',)
        verbose_name = _('work rate')
        verbose_name_plural = _('work rates')

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


class Place(WikidataModel):
    name = models.CharField(_('name'), max_length=255, blank=True)
    locative = models.CharField(_('locative'), max_length=255, blank=True, help_text=_('in…'))

    class Meta:
        verbose_name = _('place')
        verbose_name_plural = _('places')
    
    class Wikidata:
        name = 'label'

    def __str__(self):
        return self.name
