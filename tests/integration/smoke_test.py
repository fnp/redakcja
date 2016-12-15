# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from tests.integration.base import SeleniumTestCase
from django.utils.translation import ugettext as _


class SmokeTest(SeleniumTestCase):

    def test_add_book(self):
        page = self.get_main_page()
        page.select_tab(_('All'))
        assert page.tab.visible_books_count == 0
        
        page.select_tab(_('Add'))
        page.tab.put_title('Test title')
        page.tab.put_text('Test text')
        page.tab.submit()
        page.select_tab(_('All'))
        assert page.tab.visible_books_count == 1
