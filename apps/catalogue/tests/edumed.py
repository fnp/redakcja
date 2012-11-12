# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""Tests for the publishing process."""

from catalogue.test_utils import get_fixture

from mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from catalogue.models import Book
from catalogue.management import edumed

import logging
south_logger=logging.getLogger('south')
south_logger.setLevel(logging.INFO)


class EduMedTests(TestCase):
    def setUp(self):
        self.text1 = get_fixture('gim_3.1.txt')

    def test_autotag(self):
        lines = edumed.tagger(self.text1)
        for l in lines:
            print "| %s" % l
