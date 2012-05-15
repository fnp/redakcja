# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.sites.models import Site
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from slughifi import slughifi


import apiclient
from catalogue.helpers import cached_in_field
from catalogue.models import BookPublishRecord, ChunkPublishRecord
from catalogue.signals import post_publish
from catalogue.tasks import refresh_instance, book_content_updated
from catalogue.xml_tools import compile_text, split_xml
import os
import shutil
import re

class Book(models.Model):
    """ A document edited on the wiki """

    title = models.CharField(_('title'), max_length=255, db_index=True)
    slug = models.SlugField(_('slug'), max_length=128, unique=True, db_index=True)
    public = models.BooleanField(_('public'), default=True, db_index=True)
    gallery = models.CharField(_('scan gallery name'), max_length=255, blank=True)

    #wl_slug = models.CharField(_('title'), max_length=255, null=True, db_index=True, editable=False)
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_('parent'), related_name="children", editable=False)
    parent_number = models.IntegerField(_('parent number'), null=True, blank=True, db_index=True, editable=False)

    # Cache
    _short_html = models.TextField(null=True, blank=True, editable=False)
    _single = models.NullBooleanField(editable=False, db_index=True)
    _new_publishable = models.NullBooleanField(editable=False)
    _published = models.NullBooleanField(editable=False)
    _on_track = models.IntegerField(null=True, blank=True, db_index=True, editable=False)
    dc_slug = models.CharField(max_length=128, null=True, blank=True,
            editable=False, db_index=True)

    class NoTextError(BaseException):
        pass

    class Meta:
        app_label = 'catalogue'
        ordering = ['title', 'slug']
        verbose_name = _('book')
        verbose_name_plural = _('books')


    # Representing
    # ============

    def __iter__(self):
        return iter(self.chunk_set.all())

    def __getitem__(self, chunk):
        return self.chunk_set.all()[chunk]

    def __len__(self):
        return self.chunk_set.count()

    def __nonzero__(self):
        """
            Necessary so that __len__ isn't used for bool evaluation.
        """
        return True

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ("catalogue_book", [self.slug])

    def correct_about(self):
        return "http://%s%s" % (
            Site.objects.get_current().domain,
            self.get_absolute_url()
        )

    # Creating & manipulating
    # =======================

    def accessible(self, request):
        return self.public or request.user.is_authenticated()

    @classmethod
    @transaction.commit_on_success
    def create(cls, creator, text, *args, **kwargs):
        b = cls.objects.create(*args, **kwargs)
        b.chunk_set.all().update(creator=creator)
        b[0].commit(text, author=creator)
        return b

    def add(self, *args, **kwargs):
        """Add a new chunk at the end."""
        return self.chunk_set.reverse()[0].split(*args, **kwargs)

    @classmethod
    @transaction.commit_on_success
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

            slug = slughifi(title)

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

    @transaction.commit_on_success
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
                slugs = [slughifi(t) for t in titles]

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

        self.append_gallery(other, len_other)
        
        other.delete()


    def append_gallery(self, other, len_other):
        if self.gallery is None:
            self.gallery = other.gallery
            return
        if other.gallery is None:
            return
        
        def get_prefix(name):
            m = re.match(r"^([0-9])-", name)
            if m:
                return int(m.groups()[0])
            return None
        
        def set_prefix(name, prefix, always=False):
            m = not always and re.match(r"^([0-9])-", name)
            return "%1d-%s" % (prefix, m and name[2:] or name)

        files = os.listdir(os.path.join(settings.MEDIA_ROOT,
                                        settings.IMAGE_DIR, self.gallery))
        files_other = os.listdir(os.path.join(settings.MEDIA_ROOT,
                                              settings.IMAGE_DIR, other.gallery))

        prefixes = {}
        renamed_files = {}
        renamed_files_other = {}
        last_pfx = -1

        # check if all elements of my files have a prefix
        files_prefixed = True
        for f in files:
            p = get_prefix(f)
            if p:
                if p > last_pfx: last_pfx = p
            else:
                files_prefixed = False
                break

        # if not, add a 0 prefix to them
        if not files_prefixed:
            prefixes[0] = 0
            for f in files:
                renamed_files[f] = set_prefix(f, 0, True)

        # two cases here - either all are prefixed or not.
        files_other_prefixed = True
        for f in files_other:
            pfx = get_prefix(f)
            if pfx is not None:
                if not pfx in prefixes:
                    last_pfx += 1
                    prefixes[pfx] = last_pfx
                renamed_files_other[f] = set_prefix(f, prefixes[pfx])
            else:
                # ops, not all files here were prefixed.
                files_other_prefixed = False
                break

        # just set a 1- prefix to all of them
        if not files_other_prefixed:
            for f in files_other:
                renamed_files_other[f] = set_prefix(f, 1, True)

        # finally, move / rename files.
        for frm, to in renamed_files.items():
            shutil.move(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, self.gallery, frm),
                        os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, self.gallery, to))
        for frm, to in renamed_files_other.items():
            shutil.move(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, other.gallery, frm),
                        os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, self.gallery, to))            

        # and move the gallery starts
        num_files = len(files)
        for chunk in self[len(self) - len_other:]:
            chunk.gallery_start += num_files
            chunk.save()
            


    @transaction.commit_on_success
    def prepend_history(self, other):
        """Prepend history from all the other book's chunks to own."""
        assert self != other

        for i in range(len(self), len(other)):
            title = u"pusta część %d" % i
            chunk = self.add(slughifi(title), title)
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
        book_xml = self.materialize(changes=changes)

        from librarian.dcparser import BookInfo
        from librarian import NoDublinCore, ParseError, ValidationError

        try:
            bi = BookInfo.from_string(book_xml.encode('utf-8'), strict=True)
        except ParseError, e:
            raise AssertionError(_('Invalid XML') + ': ' + unicode(e))
        except NoDublinCore:
            raise AssertionError(_('No Dublin Core found.'))
        except ValidationError, e:
            raise AssertionError(_('Invalid Dublin Core') + ': ' + unicode(e))

        valid_about = self.correct_about()
        assert bi.about == valid_about, _("rdf:about is not") + " " + valid_about

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

    @cached_in_field('_short_html')
    def short_html(self):
        return render_to_string('catalogue/book_list/book.html', {'book': self})

    def book_info(self, publishable=True):
        try:
            book_xml = self.materialize(publishable=publishable)
        except self.NoTextError:
            pass
        else:
            from librarian.dcparser import BookInfo
            from librarian import NoDublinCore, ParseError, ValidationError
            try:
                return BookInfo.from_string(book_xml.encode('utf-8'))
            except (self.NoTextError, ParseError, NoDublinCore, ValidationError):
                return None

    def refresh_dc_cache(self):
        update = {
            'dc_slug': None,
        }

        info = self.book_info()
        if info is not None:
            update['dc_slug'] = info.url.slug
        Book.objects.filter(pk=self.pk).update(**update)

    def touch(self):
        # this should only really be done when text or publishable status changes
        book_content_updated.delay(self)

        update = {
            "_new_publishable": self.is_new_publishable(),
            "_published": self.is_published(),
            "_single": self.is_single(),
            "_on_track": self.get_on_track(),
            "_short_html": None,
        }
        Book.objects.filter(pk=self.pk).update(**update)
        refresh_instance(self)

    def refresh(self):
        """This should be done offline."""
        self.short_html
        self.single
        self.new_publishable
        self.published

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

    def wldocument(self, publishable=True, changes=None, parse_dublincore=True):
        from catalogue.ebook_utils import RedakcjaDocProvider
        from librarian.parser import WLDocument

        return WLDocument.from_string(
                self.materialize(publishable=publishable, changes=changes),
                provider=RedakcjaDocProvider(publishable=publishable),
                parse_dublincore=parse_dublincore)

    def publish(self, user):
        """
            Publishes a book on behalf of a (local) user.
        """
        self.assert_publishable()
        changes = self.get_current_changes(publishable=True)
        book_xml = self.materialize(changes=changes)
        apiclient.api_call(user, "books/", {"book_xml": book_xml})
        # record the publish
        br = BookPublishRecord.objects.create(book=self, user=user)
        for c in changes:
            ChunkPublishRecord.objects.create(book_record=br, change=c)
        post_publish.send(sender=br)
