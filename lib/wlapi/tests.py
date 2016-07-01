#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from nose.tools import *
from nose.core import runmodule

import wlapi


class FakeDocument:

    def __init__(self):
        self.text = "Some Text"


class TestWLAPI(object):

    def setUp(self):
        self.api = wlapi.WLAPI(
            URL="http://localhost:7000/api/",
            AUTH_REALM="WL API",
            AUTH_USER="platforma",
            AUTH_PASSWD="platforma",
        )

    def test_basic_call(self):
        assert_equal(self.api.list_books(), [])

    def test_publish_book(self):
        self.api.publish_book(FakeDocument())

if __name__ == '__main__':
    runmodule()
