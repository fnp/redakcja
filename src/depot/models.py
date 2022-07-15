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
from .legimi import legimi


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


class LegimiBookPublish(models.Model):
    book = models.ForeignKey('documents.Book', models.CASCADE)
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
    def create_for(cls, book, user):
        book.assert_publishable()
        changes = book.get_current_changes(publishable=True)
        me = cls.objects.create(book=book, user=user, created_at=now())
        for change in changes:
            me.legimichunkpublish_set.create(change=change)
        return me

    def publish(self):
        self.status = 10
        self.started_at = now()
        self.save(update_fields=['status', 'started_at'])
        try:
            changes = [
                p.change for p in
                self.legimichunkpublish_set.order_by('change__chunk__number')
            ]
            legimi.send_book(self.book, changes=changes)
            legimi.edit_sale(self.book)
        except Exception:
            self.status = 110
            self.error = traceback.format_exc()
        else:
            self.status = 100
            self.error = ''
        self.finished_at = now()
        self.save(update_fields=['status', 'finished_at', 'error'])


class LegimiChunkPublish(models.Model):
    book_publish = models.ForeignKey(LegimiBookPublish, models.CASCADE)
    change = models.ForeignKey('documents.ChunkChange', models.CASCADE)
