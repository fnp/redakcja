# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from fileupload.views import UploadView

urlpatterns = patterns('',
    url(r'^(?P<path>(?:.*/)?)$', UploadView.as_view(), name='fileupload'),
)

