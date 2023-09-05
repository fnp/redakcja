import json
import os
import tempfile
import traceback
import zipfile
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from librarian.cover import make_cover
from librarian.builders import EpubBuilder, MobiBuilder
from .publishers.legimi import Legimi
from .publishers.woblink import Woblink


class Package(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    placed_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    definition_json = models.TextField(blank=True)
    books = models.ManyToManyField('documents.Book')
    status_json = models.TextField(blank=True)
    logo = models.FileField(blank=True, upload_to='depot/logo')
    file = models.FileField(blank=True, upload_to='depot/package/')

    def save(self, *args, **kwargs):
        try:
            self.set_status(self.get_status())
        except:
            pass

        try:
            self.set_definition(self.get_definition())
        except:
            pass

        super().save(*args, **kwargs)

    def get_status(self):
        return json.loads(self.status_json)

    def set_status(self, status):
        self.status_json = json.dumps(status, indent=4, ensure_ascii=False)

    def get_definition(self):
        return json.loads(self.definition_json)

    def set_definition(self, definition):
        self.definition_json = json.dumps(definition, indent=4, ensure_ascii=False)

    def build(self):
        f = tempfile.NamedTemporaryFile(prefix='depot-', suffix='.zip', mode='wb', delete=False)
        book_count = self.books.all().count()
        with zipfile.ZipFile(f, 'w') as z:
            for i, book in enumerate(self.books.all()):
                print(f'{i}/{book_count} {book.slug}')
                self.build_for(book, z)
        f.close()
        with open(f.name, 'rb') as ff:
            self.file.save('package-{}.zip'.format(datetime.now().isoformat(timespec='seconds')), ff)
        os.unlink(f.name)

    def build_for(self, book, z):
        wldoc2 = book.wldocument(librarian2=True)
        slug = wldoc2.meta.url.slug
        for item in self.get_definition():
            wldoc = book.wldocument()
            wldoc2 = book.wldocument(librarian2=True)
            base_url = 'file://' + book.gallery_path() + '/'

            ext = item['type']

            if item['type'] == 'cover':
                kwargs = {}
                if self.logo:
                    kwargs['cover_logo'] = self.logo.path
                for k in 'format', 'width', 'height', 'cover_class':
                    if k in item:
                        kwargs[k] = item[k]
                cover = make_cover(wldoc.book_info, **kwargs)
                output = cover.output_file()
                ext = cover.ext()

            elif item['type'] == 'pdf':
                cover_kwargs = {}
                if 'cover_class' in item:
                    cover_kwargs['cover_class'] = item['cover_class']
                if self.logo:
                    cover_kwargs['cover_logo'] = self.logo.path
                cover = lambda *args, **kwargs: make_cover(*args, **kwargs, **cover_kwargs)
                output = wldoc.as_pdf(cover=cover, base_url=base_url)

            elif item['type'] == 'epub':
                cover_kwargs = {}
                if 'cover_class' in item:
                    cover_kwargs['cover_class'] = item['cover_class']
                if self.logo:
                    cover_kwargs['cover_logo'] = self.logo.path
                cover = lambda *args, **kwargs: make_cover(*args, **kwargs, **cover_kwargs)

                output = EpubBuilder(
                    cover=cover,
                    base_url=base_url,
                    fundraising=item.get('fundraising', []),
                ).build(wldoc2)

            elif item['type'] == 'mobi':
                output = MobiBuilder(
                    cover=cover,
                    base_url=base_url,
                    fundraising=item.get('fundraising', []),
                ).build(wldoc2)

            fname = f'{slug}/{slug}.'
            if 'slug' in item:
                fname += item['slug'] + '.'
            fname += ext

            z.writestr(
                fname,
                output.get_bytes()
            )


class SiteBook(models.Model):
    site = models.ForeignKey('Site', models.SET_NULL, null=True)
    book = models.ForeignKey('documents.Book', models.CASCADE)
    external_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('book', 'site'),)

    def __str__(self):
        return f'{self.site} : {self.book} : {self.external_id}'
        

class SiteBookPublish(models.Model):
    site_book = models.ForeignKey(SiteBook, models.PROTECT, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True)
    created_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=[
        (0, 'queued'),
        (10, 'running'),
        (100, 'done'),
        (110, 'error'),
    ], default=0)
    error = models.TextField(blank=True)

    @classmethod
    def create_for(cls, book, user, site):
        book.assert_publishable()
        changes = book.get_current_changes(publishable=True)
        site_book, created = SiteBook.objects.get_or_create(
            site=site, book=book
        )
        me = cls.objects.create(
            site_book=site_book, user=user, created_at=now())
        for change in changes:
            me.sitechunkpublish_set.create(change=change)
        return me

    def publish(self):
        self.status = 10
        self.started_at = now()
        self.save(update_fields=['status', 'started_at'])
        try:
            changes = [
                p.change for p in
                self.sitechunkpublish_set.order_by('change__chunk__number')
            ]

            self.site.publish(self, changes=changes)

        except Exception:
            self.status = 110
            self.error = traceback.format_exc()
        else:
            self.status = 100
            self.error = ''
        self.finished_at = now()
        self.save(update_fields=['status', 'finished_at', 'error'])


class SiteChunkPublish(models.Model):
    book_publish = models.ForeignKey(SiteBookPublish, models.CASCADE)
    change = models.ForeignKey('documents.ChunkChange', models.CASCADE)


class Site(models.Model):
    name = models.CharField(max_length=255)
    site_type = models.CharField(max_length=32, choices=[
        ('legimi', 'Legimi'),
        ('woblink', 'Woblink'),
    ])
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    publisher_handle = models.CharField(max_length=255, blank=True)
    description_add = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_texts(self):
        return [t.text for t in self.mediainserttext_set.all()]

    def get_price(self, words, pages):
        price_obj = self.pricelevel_set.exclude(
            min_pages__gt=pages
        ).exclude(
            min_words__gt=words
        ).order_by('-price').first()
        if price_obj is None:
            return None
        return price_obj.price

    def get_publisher(self):
        if self.site_type == 'legimi':
            pub_class = Legimi
        elif self.site_type == 'woblink':
            pub_class = Woblink
        return pub_class(self.username, self.password, self.publisher_handle)

    def publish(self, site_book_publish, changes):
        self.get_publisher().send_book(
            site_book_publish,
            changes=changes,
        )

    def can_publish(self, book):
        return self.get_publisher().can_publish(self, book)

    def get_last(self, book):
        return SiteBookPublish.objects.filter(
            site_book__site=self, site_book__book=book
        ).order_by('-created_at').first()

    def get_external_id_for_book(self, book):
        site_book = self.sitebook_set.filter(book=book).first()
        return (site_book and site_book.external_id) or ''

class PriceLevel(models.Model):
    site = models.ForeignKey(Site, models.CASCADE)
    min_pages = models.IntegerField(null=True, blank=True)
    min_words = models.IntegerField(null=True, blank=True)
    price = models.IntegerField()

    class Meta:
        ordering = ('price',)


class MediaInsertText(models.Model):
    site = models.ForeignKey(Site, models.CASCADE)
    ordering = models.IntegerField()
    text = models.TextField()

    class Meta:
        ordering = ('ordering',)
