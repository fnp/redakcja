# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url


urlpatterns = patterns('cover.views',
    url(r'^preview/$', 'preview_from_xml', name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/$', 'preview', name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/(?P<chunk>[^/]+)/$',
            'preview', name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/(?P<chunk>[^/]+)/(?P<rev>\d+)/$',
            'preview', name='cover_preview'),

    url(r'^image/$', 'image_list', name='cover_image_list'),
    url(r'^image/(?P<pk>\d+)/?$', 'image', name='cover_image'),
    url(r'^image/(?P<pk>\d+)/file/', 'image_file', name='cover_file'),
    url(r'^add_image/$', 'add_image', name='cover_add_image'),
)
