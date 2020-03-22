# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""XmlUpdater tests."""

from documents.test_utils import get_fixture
from django.test import TestCase
from django.contrib.auth.models import User
from documents.models import Book
from documents.management import XmlUpdater
from librarian import DCNS


class XmlUpdaterTests(TestCase):
    class SimpleUpdater(XmlUpdater):
        @XmlUpdater.fixes_elements('.//' + DCNS('title'))
        def fix_title(element, **kwargs):
            element.text = element.text + " fixed"
            return True

    def setUp(self):
        self.user = User.objects.create(username='tester')
        text = get_fixture('chunk1.xml')
        Book.create(self.user, text, slug='test-book')
        self.title = "Do M***"

    def test_xml_updater(self):
        self.SimpleUpdater().run(self.user)
        self.assertEqual(
            Book.objects.get(slug='test-book').wldocument(
                publishable=False).book_info.title,
            self.title + " fixed"
            )
