# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from urllib import FancyURLopener
from django.contrib.sites.models import Site


class URLOpener(urllib.FancyURLopener):
    @property
    def version(self):
        return 'FNP Redakcja (http://%s)' % Site.objects.get_current()
