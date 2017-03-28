# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from fileupload.views import UploadView

urlpatterns = (
    url(r'^(?P<path>(?:.*/)?)$', UploadView.as_view(), name='fileupload'),
)
