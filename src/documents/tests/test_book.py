# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""Tests for manipulating books in the catalogue."""

from django.test import TestCase
from django.contrib.auth.models import User
from documents.models import Book


class ManipulationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.book1 = Book.create(self.user, 'book 1', slug='book1')
        self.book2 = Book.create(self.user, 'book 2', slug='book2')

    def test_append(self):
        self.book1.append(self.book2)
        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(len(self.book1), 2)

    def test_append_to_self(self):
        with self.assertRaises(AssertionError):
            self.book1.append(Book.objects.get(pk=self.book1.pk))
        self.assertEqual(Book.objects.all().count(), 2)
        self.assertEqual(len(self.book1), 1)

    def test_prepend_history(self):
        self.book1.prepend_history(self.book2)
        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(len(self.book1), 1)
        self.assertEqual(self.book1.materialize(), 'book 1')

    def test_prepend_history_to_self(self):
        with self.assertRaises(AssertionError):
            self.book1.prepend_history(self.book1)
        self.assertEqual(Book.objects.all().count(), 2)
        self.assertEqual(self.book1.materialize(), 'book 1')
        self.assertEqual(self.book2.materialize(), 'book 2')

    def test_split_book(self):
        self.book1.chunk_set.create(number=2, title='Second chunk',
                slug='book3')
        self.book1[1].commit('I survived!')
        self.assertEqual(len(self.book1), 2)
        self.book1.split()
        self.assertEqual(set([b.slug for b in Book.objects.all()]),
                set(['book2', '1', 'book3']))
        self.assertEqual(
                Book.objects.get(slug='book3').materialize(),
                'I survived!')
