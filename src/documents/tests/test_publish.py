# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""Tests for the publishing process."""

from documents.test_utils import get_fixture

from mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from documents.models import Book


class PublishTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.text1 = get_fixture('chunk1.xml')
        self.book = Book.create(self.user, self.text1, slug='test-book')

    @patch('apiclient.api_call')
    def test_unpublishable(self, api_call):
        with self.assertRaises(AssertionError):
            self.book.publish(self.user)

    @patch('apiclient.api_call')
    def test_publish(self, api_call):
        self.book[0].head.set_publishable(True)
        self.book.publish(self.user)
        api_call.assert_called_with(self.user, 'books/', {"book_xml": self.text1, "days": 0}, beta=False)

    @patch('apiclient.api_call')
    def test_publish_multiple(self, api_call):
        self.book[0].head.set_publishable(True)
        self.book[0].split(slug='part-2')
        self.book[1].commit(get_fixture('chunk2.xml'))
        self.book[1].head.set_publishable(True)
        self.book.publish(self.user)
        api_call.assert_called_with(self.user, 'books/', {"book_xml": get_fixture('expected.xml'), "days": 0}, beta=False)
