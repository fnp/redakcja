from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    name = models.CharField(max_length=255)
    year_of_death = models.SmallIntegerField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(null=True, blank=True, choices=[
        (1, _('Alive')),
        (2, _('Dead')),
        (3, _('Long dead')),
        (4, _('Unknown')),
    ])

    def __str__(self):
        return self.name


class Book(models.Model):
    uri = models.CharField(max_length=255)

    authors = models.ManyToManyField(Author, blank=True)
    translators = models.ManyToManyField(Author, related_name='translated_book_set', related_query_name='translated_book', blank=True)
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=3)
    based_on = models.ForeignKey('self', models.PROTECT, related_name='translation', null=True, blank=True)

    scans_source = models.CharField(max_length=255, blank=True)
    text_source = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(default=0, choices=[
        (0, _('Low')),
        (1, _('Medium')),
        (2, _('High')),
    ])

    def __str__(self):
        return self.title
