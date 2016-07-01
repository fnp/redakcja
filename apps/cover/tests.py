# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from nose.tools import *
from django.test import TestCase
from cover.forms import FlickrForm


class FlickrTests(TestCase):
    def test_flickr(self):
        form = FlickrForm({"source_url": "https://www.flickr.com/photos/rczajka/6941928577/in/photostream"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['source_url'], "https://www.flickr.com/photos/rczajka/6941928577/")
        self.assertEqual(form.cleaned_data['author'], "rczajka@Flickr")
        self.assertEqual(form.cleaned_data['title'], u"Pirate Stańczyk")
        self.assertEqual(form.cleaned_data['license_name'], "CC BY 2.0")
        self.assertEqual(form.cleaned_data['license_url'], "http://creativecommons.org/licenses/by/2.0/deed.en")
        self.assertEqual(form.cleaned_data['download_url'],
                         "https://farm8.staticflickr.com/7069/6941928577_415844c58e_o.jpg")
