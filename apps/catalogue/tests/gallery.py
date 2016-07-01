# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""Tests for galleries of scans."""

from os.path import join, basename, exists
from os import makedirs, listdir
from django.test import TestCase
from django.contrib.auth.models import User
from catalogue.models import Book
from tempfile import mkdtemp
from django.conf import settings


class GalleryAppendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.book1 = Book.create(self.user, 'book 1', slug='book1')
        self.book1.chunk_set.create(number=2, title='Second chunk', slug='book 1 / 2')
        c = self.book1[1]
        c.gallery_start = 3

        self.scandir = join(settings.MEDIA_ROOT, settings.IMAGE_DIR)
        if not exists(self.scandir):
            makedirs(self.scandir)

    def make_gallery(self, book, files):
        d = mkdtemp('gallery', dir=self.scandir)
        for named, cont in files.items():
            f = open(join(d, named), 'w')
            f.write(cont)
            f.close()
        book.gallery = basename(d)

    def test_both_indexed(self):
        self.book2 = Book.create(self.user, 'book 2', slug='book2')
        self.book2.chunk_set.create(number=2, title='Second chunk of second book', slug='book 2 / 2')

        c = self.book2[1]
        c.gallery_start = 3
        c.save()

        print "gallery starts:", self.book2[0].gallery_start, self.book2[1].gallery_start

        self.make_gallery(self.book1, {
            '1-0001_1l': 'aa',
            '1-0001_2r': 'bb',
            '1-0002_1l': 'cc',
            '1-0002_2r': 'dd',
        })

        self.make_gallery(self.book2, {
            '1-0001_1l': 'dd',  # the same, should not be moved
            '1-0001_2r': 'ff',
            '2-0002_1l': 'gg',
            '2-0002_2r': 'hh',
        })

        self.book1.append(self.book2)

        files = listdir(join(self.scandir, self.book1.gallery))
        files.sort()
        print files
        self.assertEqual(files, [
            '1-0001_1l',
            '1-0001_2r',
            '1-0002_1l',
            '1-0002_2r',
            #            '2-0001_1l',
            '2-0001_2r',
            '3-0002_1l',
            '3-0002_2r',
            ])

        self.assertEqual((4, 6), (self.book1[2].gallery_start, self.book1[3].gallery_start))

    def test_none_indexed(self):
        self.book2 = Book.create(self.user, 'book 2', slug='book2')
        self.make_gallery(self.book1, {
            '0001_1l': 'aa',
            '0001_2r': 'bb',
            '0002_1l': 'cc',
            '0002_2r': 'dd',
        })

        self.make_gallery(self.book2, {
            '0001_1l': 'ee',
            '0001_2r': 'ff',
            '0002_1l': 'gg',
            '0002_2r': 'hh',
        })

        self.book1.append(self.book2)

        files = listdir(join(self.scandir, self.book1.gallery))
        files.sort()
        print files
        self.assertEqual(files, [
            '0-0001_1l',
            '0-0001_2r',
            '0-0002_1l',
            '0-0002_2r',
            '1-0001_1l',
            '1-0001_2r',
            '1-0002_1l',
            '1-0002_2r',
            ])

    def test_none_indexed2(self):
        self.book2 = Book.create(self.user, 'book 2', slug='book2')
        self.make_gallery(self.book1, {
            '1-0001_1l': 'aa',
            '1-0001_2r': 'bb',
            '1002_1l': 'cc',
            '1002_2r': 'dd',
        })

        self.make_gallery(self.book2, {
            '0001_1l': 'ee',
            '0001_2r': 'ff',
            '0002_1l': 'gg',
            '0002_2r': 'hh',
        })

        self.book1.append(self.book2)

        files = listdir(join(self.scandir, self.book1.gallery))
        files.sort()
        print files
        self.assertEqual(files, [
            '0-1-0001_1l',
            '0-1-0001_2r',
            '0-1002_1l',
            '0-1002_2r',
            '1-0001_1l',
            '1-0001_2r',
            '1-0002_1l',
            '1-0002_2r',
            ])
