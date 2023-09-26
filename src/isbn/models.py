from django.apps import apps
from django.db import models
from lxml import etree
import requests
from .product_forms import FORMS


class IsbnPool(models.Model):
    PURPOSE_GENERAL = 'GENERAL'
    PURPOSE_WL = 'WL'
    PURPOSE_CHOICES = (
        (PURPOSE_WL, 'Wolne Lektury'),
        (PURPOSE_GENERAL, 'Ogólne'),
    )

    prefix = models.CharField(max_length=10)
    suffix_from = models.IntegerField()
    suffix_to = models.IntegerField()
    ref_from = models.IntegerField()
    purpose = models.CharField(max_length=8, choices=PURPOSE_CHOICES)

    def __str__(self):
        return '-'.join((
            self.prefix[:3],
            self.prefix[3:5],
            self.prefix[5:],
            'X' * (12 - len(self.prefix)),
            'X'
        ))

    @staticmethod
    def check_digit(prefix12):
        digits = [int(d) for d in prefix12]
        return str((-sum(digits[0::2]) + 7 * sum(digits[1::2])) % 10)
    
    def get_code(self, suffix, dashes=False):
        suffix_length = 12 - len(self.prefix)
        suffix_str = f'{suffix:0{suffix_length}d}'
        prefix12 = self.prefix + suffix_str
        check_digit = self.check_digit(prefix12)
        if dashes:
            isbn = '-'.join((
                self.prefix[:3],
                self.prefix[3:5],
                self.prefix[5:],
                suffix_str,
                check_digit
            ))
        else:
            isbn = ''.join((
                prefix12, check_digit
            ))
        return isbn

    
    @property
    def size(self):
        return self.suffix_to - self.suffix_from + 1

    @property
    def entries(self):
        return self.isbn_set.count()
    
    @property
    def fill_percentage(self):
        return 100 * self.entries / self.size

    def bn_record_id_for(self, suffix):
        return self.ref_from + suffix
    
    def import_all_bn_data(self):
        for suffix in range(self.suffix_from, self.suffix_to + 1):
            print(suffix)
            self.import_bn_data_for(suffix)
    
    def import_bn_data_for(self, suffix):
        record_id = self.bn_record_id_for(suffix)
        content = requests.get(
            f'https://e-isbn.pl/IsbnWeb/record/export_onix.xml?record_id={record_id}').content
        elem = etree.fromstring(content)
        product = elem.find('{http://ns.editeur.org/onix/3.0/reference}Product')
        if product is not None:
            isbn, created = self.isbn_set.get_or_create(
                suffix=suffix
            )
            isbn.bn_data = etree.tostring(product, pretty_print=True, encoding='unicode')
            isbn.save(update_fields=['bn_data'])


class Isbn(models.Model):
    pool = models.ForeignKey(IsbnPool, models.PROTECT)
    suffix = models.IntegerField()
    datestamp = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        'catalogue.Book', models.PROTECT, null=True, blank=True
    )
    form = models.CharField(
        max_length=32, choices=[
            (form, form)
            for form, config in FORMS
        ], null=True, blank=True
    )
    bn_data = models.TextField(blank=True)
    wl_data = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['pool', 'suffix']
        unique_together = ['pool', 'suffix']

    def __str__(self):
        return self.get_code(True)
        
    def get_code(self, dashes=True):
        return self.pool.get_code(self.suffix, dashes=dashes)

    @classmethod
    def import_from_documents(cls):
        Book = apps.get_model('documents', 'Book')
        for book in Book.objects.all():
            try:
                catalogue_book = book.catalogue_book
                if catalogue_book is None:
                    continue
            except:
                continue
            try:
                meta = book.wldocument(publishable=False, librarian2=True).meta
            except:
                continue
            for form in ('html', 'txt', 'pdf', 'epub', 'mobi'):
                isbn = getattr(meta, f'isbn_{form}')
                if isbn is not None:
                    parts = isbn.split('-')
                    assert parts[0] == 'ISBN'
                    suffix = int(parts[-2])
                    prefix = ''.join(parts[1:-2])
                    pool = IsbnPool.objects.get(prefix=prefix)
                    isbn, created = pool.isbn_set.get_or_create(
                        suffix=suffix,
                    )
                    if isbn.book is None:
                        isbn.book = catalogue_book
                    else:
                        assert isbn.book is catalogue_book
                    if isbn.form is None:
                        isbn.form = form
                    else:
                        assert isbn.form == form
                    isbn.save(update_fields=['book', 'form'])
