from nose.tools import *
from mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from catalogue.models import Book, BookPublishRecord

class PublishTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.book = Book.create(self.user, 'publish me')

    @patch('apiclient.api_call')
    def test_unpublishable(self, api_call):
        with self.assertRaises(Book.NoTextError):
            self.book.publish(self.user)

    @patch('apiclient.api_call')
    def test_publish(self, api_call):
        self.book[0].head.set_publishable(True)
        self.book.publish(self.user)
        api_call.assert_called_with(self.user, 'books', {"book_xml": 'publish me'})

    @patch('apiclient.api_call')
    def test_publish_multiple(self, api_call):
        self.book[0].head.set_publishable(True)
        self.book[0].split(slug='part-2')
        self.book[1].commit('take me \n<!-- TRIM_BEGIN -->\n too')
        self.book[1].head.set_publishable(True)
        self.book.publish(self.user)
        api_call.assert_called_with(self.user, 'books', {"book_xml": 'publish me\n too'})


class ManipulationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.book1 = Book.create(self.user, 'book 1')
        self.book2 = Book.create(self.user, 'book 2')

    def test_append(self):
        self.book1.append(self.book2)
        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(len(self.book1), 2)

    def test_append_to_self(self):
        with self.assertRaises(AssertionError):
            self.book1.append(Book.objects.get(pk=self.book1.pk))
        self.assertEqual(Book.objects.all().count(), 2)
        self.assertEqual(len(self.book1), 1)
