import os
import subprocess
import uuid
from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from . import conversion
from . import document
from . import utils


class Source(models.Model):
    name = models.CharField(_('name'), max_length=1024)
    notes = models.TextField(blank=True, help_text=_('private'))
    wikisource = models.CharField(max_length=1024, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('source', args=[self.pk])

    def touch(self):
        self.modified_at = now()
        self.save(update_fields=['modified_at'])
    
    def get_upload_directory(self):
        return f'sources/upload/{self.pk}/'

    def get_view_directory(self):
        return f'sources/view/{self.pk}/'

    def get_ocr_directory(self):
        return f'sources/ocr/{self.pk}/'

    def has_upload_files(self):
        d = os.path.join(settings.MEDIA_ROOT, self.get_upload_directory())
        return os.path.isdir(d) and os.listdir(d)
    
    def get_view_files(self):
        d = self.get_view_directory()
        return [
            d + name
            for name in sorted(os.listdir(
                    os.path.join(settings.MEDIA_ROOT, d)
            ))
        ]

    def has_view_files(self):
        d = os.path.join(settings.MEDIA_ROOT, self.get_view_directory())
        return os.path.isdir(d) and os.listdir(d)
    
    def get_ocr_files(self):
        d = os.path.join(settings.MEDIA_ROOT, self.get_ocr_directory())
        return [
            d + name
            for name in sorted(os.listdir(d))
        ]

    def has_ocr_files(self):
        d = os.path.join(settings.MEDIA_ROOT, self.get_ocr_directory())
        return os.path.isdir(d) and os.listdir(d)

    def process(self):
        processed_at = now()
        updir = os.path.join(
            settings.MEDIA_ROOT,
            self.get_upload_directory()
        )
        view_dir = os.path.join(
            settings.MEDIA_ROOT,
            self.get_view_directory()
        )
        ocr_dir = os.path.join(
            settings.MEDIA_ROOT,
            self.get_ocr_directory()
        )
        with utils.replace_dir(view_dir) as d:
            self.build_view_directory(updir, d)
        with utils.replace_dir(ocr_dir) as d:
            self.build_ocr_directory(updir, d)
        self.processed_at = processed_at
        self.save(update_fields=['processed_at'])
    
    def build_view_directory(self, srcpath, targetpath):
        for source_file_name in os.listdir(srcpath):
            print(source_file_name)
            src = os.path.join(srcpath, source_file_name)
            ext = source_file_name.rsplit('.', 1)[-1].lower()
            if ext in ('png', 'jpg', 'jpeg'):
                conversion.resize_image(src, targetpath)
                # cp?
                # maybe resize
            elif ext in ('tiff', 'tif'):
                conversion.convert_image(src, targetpath)
            elif ext == 'pdf':
                conversion.convert_pdf(src, targetpath)
            elif ext == 'djvu':
                conversion.convert_djvu(src, targetpath)
            else:
                pass

    def build_ocr_directory(self, srcpath, targetpath):
        for source_file_name in os.listdir(srcpath):
            print(source_file_name)
            subprocess.run([
                'tesseract',
                os.path.join(srcpath, source_file_name),
                os.path.join(targetpath, source_file_name),
                '-l', 'pol'
            ])


class BookSource(models.Model):
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    source = models.ForeignKey(Source, models.CASCADE)
    page_start = models.IntegerField(null=True, blank=True)
    page_end = models.IntegerField(null=True, blank=True)
        
    class Meta:
        ordering = ('page_start',)

    def __str__(self):
        return f'{self.source} -> {self.book}'

    def get_absolute_url(self):
        return reverse('source_book_prepare', args=[self.pk])

    def get_view_files(self):
        # TODO: won't work for PDFs.
        files = self.source.get_view_files()
        if self.page_end:
            files = files[:self.page_end]
        if self.page_start:
            files = files[self.page_start - 1:]
        return files

    def get_ocr_files(self):
        # TODO: won't work for PDFs.
        files = self.source.get_ocr_files()
        if self.page_end:
            files = files[:self.page_end]
        if self.page_start:
            files = files[self.page_start - 1:]
        return files

    def get_document(self):
        return self.book.document_books.first()
        
    def prepare_document(self, user=None):
        DBook = apps.get_model('documents', 'Book')
        texts = document.build_document_texts(self)

        dbook = self.get_document()
        if dbook is None:
            dbook = DBook.create(
                user, texts[0],
                title=self.book.title,
                slug=str(uuid.uuid4()),
            )
        else:
            dbook[0].commit(text=texts[0], description='OCR', author=user)
        for text in texts[1:]:
            dbook[0].commit(text=text, description='OCR', author=user)

        dbook[0].head.set_publishable(True)
        return dbook

