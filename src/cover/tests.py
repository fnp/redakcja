# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.test import TestCase
from cover.forms import FlickrForm


class FlickrTests(TestCase):
    def test_flickr(self):
        form = FlickrForm({"source_url": "https://www.flickr.com/photos/rczajka/6941928577/in/photostream"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['source_url'], "https://www.flickr.com/photos/rczajka/6941928577/")
        self.assertEqual(form.cleaned_data['author'], "Radek Czajka@Flickr")
        self.assertEqual(form.cleaned_data['title'], u"Pirate Stańczyk")
        self.assertEqual(form.cleaned_data['license_name'], "CC BY 2.0")
        self.assertEqual(form.cleaned_data['license_url'], "https://creativecommons.org/licenses/by/2.0/")
        self.assertTrue('.staticflickr.com' in form.cleaned_data['download_url'])
