# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import apps
from django.core.files.base import ContentFile
from django.contrib.sites.models import Site
from django.db import connection, models, transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from slugify import slugify
from librarian.cover import make_cover
from librarian.dcparser import BookInfo

import apiclient
from documents.helpers import cached_in_field, GalleryMerger
from documents.models import BookPublishRecord, ChunkPublishRecord, Project
from documents.signals import post_publish
from documents.xml_tools import compile_text, split_xml
from cover.models import Image
from io import BytesIO
import os
import shutil
import re


class Book(models.Model):
    """ A document edited on the wiki """

    title = models.CharField(_('title'), max_length=255, db_index=True)
    slug = models.SlugField(_('slug'), max_length=128, unique=True, db_index=True)
    public = models.BooleanField(_('public'), default=True, db_index=True)
    gallery = models.CharField(_('scan gallery name'), max_length=255, blank=True)
    project = models.ForeignKey(Project, models.SET_NULL, null=True, blank=True)

    parent = models.ForeignKey('self', models.SET_NULL, null=True, blank=True, verbose_name=_('parent'), related_name="children", editable=False)
    parent_number = models.IntegerField(_('parent number'), null=True, blank=True, db_index=True, editable=False)

    # Cache
    _single = models.BooleanField(editable=False, null=True, db_index=True)
    _new_publishable = models.BooleanField(editable=False, null=True)
    _published = models.BooleanField(editable=False, null=True)
    _on_track = models.IntegerField(null=True, blank=True, db_index=True, editable=False)
    dc_cover_image = models.ForeignKey(Image, blank=True, null=True,
        db_index=True, on_delete=models.SET_NULL, editable=False)
    dc = models.JSONField(null=True, editable=False)
    cover = models.FileField(blank=True, upload_to='documents/cover')
    catalogue_book = models.ForeignKey(
        'catalogue.Book',
        models.DO_NOTHING,
        to_field='slug',
        null=True, blank=True,
        db_constraint=False,
        editable=False, db_index=True,
        related_name='document_books',
        related_query_name='document_book',
    )

    class NoTextError(BaseException):
        pass

    class Meta:
        app_label = 'documents'
        ordering = ['title', 'slug']
        verbose_name = _('book')
        verbose_name_plural = _('books')

    @classmethod
    def get_visible_for(cls, user):
        qs = cls.objects.all()
        if not user.is_authenticated:
            qs = qs.filter(public=True)
        return qs

    @staticmethod
    def q_dc(field, field_plural, value, prefix=''):
        if connection.features.supports_json_field_contains:
            return models.Q(**{f'{prefix}dc__{field_plural}__contains': value})
        else:
            return models.Q(**{f'{prefix}dc__{field}': value})
            
    
    # Representing
    # ============

    def __iter__(self):
        return iter(self.chunk_set.all())

    def __getitem__(self, chunk):
        return self.chunk_set.all()[chunk]

    def __len__(self):
        return self.chunk_set.count()

    def __bool__(self):
        """
            Necessary so that __len__ isn't used for bool evaluation.
        """
        return True

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("documents_book", args=[self.slug])

    def correct_about(self):
        return "http://%s%s" % (
            Site.objects.get_current().domain,
            self.get_absolute_url()
        )

    def gallery_path(self):
        return os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, self.gallery)

    def gallery_url(self):
        return '%s%s%s/' % (settings.MEDIA_URL, settings.IMAGE_DIR, self.gallery)

    # Creating & manipulating
    # =======================

    def accessible(self, request):
        return self.public or request.user.is_authenticated

    @classmethod
    @transaction.atomic
    def create(cls, creator, text, *args, **kwargs):
        b = cls.objects.create(*args, **kwargs)
        b.chunk_set.all().update(creator=creator)
        b[0].commit(text, author=creator)
        return b

    def add(self, *args, **kwargs):
        """Add a new chunk at the end."""
        return self.chunk_set.reverse()[0].split(*args, **kwargs)

    @classmethod
    @transaction.atomic
    def import_xml_text(cls, text=u'', previous_book=None,
                commit_args=None, **kwargs):
        """Imports a book from XML, splitting it into chunks as necessary."""
        texts = split_xml(text)
        if previous_book:
            instance = previous_book
        else:
            instance = cls(**kwargs)
            instance.save()

        # if there are more parts, set the rest to empty strings
        book_len = len(instance)
        for i in range(book_len - len(texts)):
            texts.append((u'pusta część %d' % (i + 1), u''))

        i = 0
        for i, (title, text) in enumerate(texts):
            if not title:
                title = u'część %d' % (i + 1)

            slug = slugify(title)

            if i < book_len:
                chunk = instance[i]
                chunk.slug = slug[:50]
                chunk.title = title[:255]
                chunk.save()
            else:
                chunk = instance.add(slug, title)

            chunk.commit(text, **commit_args)

        return instance

    def make_chunk_slug(self, proposed):
        """ 
            Finds a chunk slug not yet used in the book.
        """
        slugs = set(c.slug for c in self)
        i = 1
        new_slug = proposed[:50]
        while new_slug in slugs:
            new_slug = "%s_%d" % (proposed[:45], i)
            i += 1
        return new_slug

    @transaction.atomic
    def append(self, other, slugs=None, titles=None):
        """Add all chunks of another book to self."""
        assert self != other

        number = self[len(self) - 1].number + 1
        len_other = len(other)
        single = len_other == 1

        if slugs is not None:
            assert len(slugs) == len_other
        if titles is not None:
            assert len(titles) == len_other
            if slugs is None:
                slugs = [slugify(t) for t in titles]

        for i, chunk in enumerate(other):
            # move chunk to new book
            chunk.book = self
            chunk.number = number

            if titles is None:
                # try some title guessing
                if other.title.startswith(self.title):
                    other_title_part = other.title[len(self.title):].lstrip(' /')
                else:
                    other_title_part = other.title

                if single:
                    # special treatment for appending one-parters:
                    # just use the guessed title and original book slug
                    chunk.title = other_title_part
                    if other.slug.startswith(self.slug):
                        chunk.slug = other.slug[len(self.slug):].lstrip('-_')
                    else:
                        chunk.slug = other.slug
                else:
                    chunk.title = ("%s, %s" % (other_title_part, chunk.title))[:255]
            else:
                chunk.slug = slugs[i]
                chunk.title = titles[i]

            chunk.slug = self.make_chunk_slug(chunk.slug)
            chunk.save()
            number += 1
        assert not other.chunk_set.exists()

        gm = GalleryMerger(self.gallery, other.gallery)
        self.gallery = gm.merge()

        # and move the gallery starts
        if gm.was_merged:
                for chunk in self[len(self) - len_other:]:
                        old_start = chunk.gallery_start or 1
                        chunk.gallery_start = old_start + gm.dest_size - gm.num_deleted
                        chunk.save()

        other.delete()


    @transaction.atomic
    def prepend_history(self, other):
        """Prepend history from all the other book's chunks to own."""
        assert self != other

        for i in range(len(self), len(other)):
            title = u"pusta część %d" % i
            chunk = self.add(slugify(title), title)
            chunk.commit('')

        for i in range(len(other)):
            self[i].prepend_history(other[0])

        assert not other.chunk_set.exists()
        other.delete()

    def split(self):
        """Splits all the chunks into separate books."""
        self.title
        for chunk in self:
            book = Book.objects.create(title=chunk.title, slug=chunk.slug,
                    public=self.public, gallery=self.gallery)
            book[0].delete()
            chunk.book = book
            chunk.number = 1
            chunk.save()
        assert not self.chunk_set.exists()
        self.delete()

    # State & cache
    # =============

    def last_published(self):
        try:
            return self.publish_log.all()[0].timestamp
        except IndexError:
            return None

    def assert_publishable(self):
        assert self.chunk_set.exists(), _('No chunks in the book.')
        try:
            changes = self.get_current_changes(publishable=True)
        except self.NoTextError:
            raise AssertionError(_('Not all chunks have publishable revisions.'))

        from librarian import NoDublinCore, ParseError, ValidationError

        try:
            bi = self.wldocument(changes=changes, strict=True).book_info
        except ParseError as e:
            raise AssertionError(_('Invalid XML') + ': ' + str(e))
        except NoDublinCore:
            raise AssertionError(_('No Dublin Core found.'))
        except ValidationError as e:
            raise AssertionError(_('Invalid Dublin Core') + ': ' + str(e))

        valid_about = self.correct_about()
        assert bi.about == valid_about, _("rdf:about is not") + " " + valid_about

    def publishable_error(self):
        try:
            return self.assert_publishable()
        except AssertionError as e:
            return e
        else:
            return None

    def hidden(self):
        return self.slug.startswith('.')

    def is_new_publishable(self):
        """Checks if book is ready for publishing.

        Returns True if there is a publishable version newer than the one
        already published.

        """
        new_publishable = False
        if not self.chunk_set.exists():
            return False
        for chunk in self:
            change = chunk.publishable()
            if not change:
                return False
            if not new_publishable and not change.publish_log.exists():
                new_publishable = True
        return new_publishable
    new_publishable = cached_in_field('_new_publishable')(is_new_publishable)

    def is_published(self):
        return self.publish_log.exists()
    published = cached_in_field('_published')(is_published)

    def get_on_track(self):
        if self.published:
            return -1
        stages = [ch.stage.ordering if ch.stage is not None else 0
                    for ch in self]
        if not len(stages):
            return 0
        return min(stages)
    on_track = cached_in_field('_on_track')(get_on_track)

    def is_single(self):
        return len(self) == 1
    single = cached_in_field('_single')(is_single)

    def book_info(self, publishable=True):
        try:
            book_xml = self.materialize(publishable=publishable)
        except self.NoTextError:
            pass
        else:
            from librarian.dcparser import BookInfo
            from librarian import NoDublinCore, ParseError, ValidationError
            try:
                return BookInfo.from_bytes(book_xml.encode('utf-8'))
            except (self.NoTextError, ParseError, NoDublinCore, ValidationError):
                return None

    def refresh_dc_cache(self):
        update = {
            'catalogue_book_id': None,
            'dc_cover_image': None,
        }

        info = self.book_info()
        if info is not None:
            update['catalogue_book_id'] = info.url.slug
            if info.cover_source:
                try:
                    image = Image.objects.get(pk=int(info.cover_source.rstrip('/').rsplit('/', 1)[-1]))
                except:
                    pass
                else:
                    if info.cover_source == image.get_full_url():
                        update['dc_cover_image'] = image
            update['dc'] = info.to_dict()
        Book.objects.filter(pk=self.pk).update(**update)

    def touch(self):
        update = {
            "_new_publishable": self.is_new_publishable(),
            "_published": self.is_published(),
            "_single": self.is_single(),
            "_on_track": self.get_on_track(),
        }
        Book.objects.filter(pk=self.pk).update(**update)
        self.refresh_dc_cache()
        self.build_cover()

    def build_cover(self):
        width, height = 212, 300
        try:
            xml = self.materialize(publishable=True).encode('utf-8')
            info = BookInfo.from_bytes(xml)
            cover = make_cover(info, width=width, height=height)
            out = BytesIO()
            ext = cover.ext()
            cover.save(out)
            self.cover.save(f'{self.slug}.{ext}', out, save=False)
            type(self).objects.filter(pk=self.pk).update(cover=self.cover)
        except:
            type(self).objects.filter(pk=self.pk).update(cover='')

    # Materializing & publishing
    # ==========================

    def get_current_changes(self, publishable=True):
        """
            Returns a list containing one Change for every Chunk in the Book.
            Takes the most recent revision (publishable, if set).
            Throws an error, if a proper revision is unavailable for a Chunk.
        """
        if publishable:
            changes = [chunk.publishable() for chunk in self]
        else:
            changes = [chunk.head for chunk in self if chunk.head is not None]
        if None in changes:
            raise self.NoTextError('Some chunks have no available text.')
        return changes

    def materialize(self, publishable=False, changes=None):
        """ 
            Get full text of the document compiled from chunks.
            Takes the current versions of all texts
            or versions most recently tagged for publishing,
            or a specified iterable changes.
        """
        if changes is None:
            changes = self.get_current_changes(publishable)
        return compile_text(change.materialize() for change in changes)

    def wldocument(self, publishable=True, changes=None, 
                   parse_dublincore=True, strict=False, librarian2=False):
        from documents.ebook_utils import RedakcjaDocProvider
        from librarian.parser import WLDocument
        from librarian.document import WLDocument as WLDocument2

        provider = RedakcjaDocProvider(publishable=publishable)
        xml = self.materialize(publishable=publishable, changes=changes).encode('utf-8')
        
        if librarian2:
            return WLDocument2(
                BytesIO(xml),
                provider=provider)
        return WLDocument.from_bytes(
                xml,
                provider=provider,
                parse_dublincore=parse_dublincore,
                strict=strict)

    def publish(self, user, fake=False, host=None, days=0, beta=False, hidden=False):
        """
            Publishes a book on behalf of a (local) user.
        """
        self.assert_publishable()
        changes = self.get_current_changes(publishable=True)
        if not fake:
            book_xml = self.materialize(changes=changes)
            data = {"book_xml": book_xml, "days": days, "hidden": hidden}
            if host:
                data['gallery_url'] = host + self.gallery_url()
            apiclient.api_call(user, "books/", data, beta=beta)
        if not beta:
            # record the publish
            br = BookPublishRecord.objects.create(book=self, user=user)
            for c in changes:
                ChunkPublishRecord.objects.create(book_record=br, change=c)
            if not self.public and days == 0:
                self.public = True
                self.save()
            if self.public and days > 0:
                self.public = False
                self.save()
            post_publish.send(sender=br)

    def latex_dir(self):
        doc = self.wldocument()
        return doc.latex_dir(cover=True, ilustr_path=self.gallery_path())
