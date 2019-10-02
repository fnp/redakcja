# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^preview/$', views.preview_from_xml, name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/$', views.preview, name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/(?P<chunk>[^/]+)/$',
            views.preview, name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/(?P<chunk>[^/]+)/(?P<rev>\d+)/$',
            views.preview, name='cover_preview'),

    url(r'^image/$', views.image_list, name='cover_image_list'),
    url(r'^image/(?P<pk>\d+)/?$', views.image, name='cover_image'),
    url(r'^image/(?P<pk>\d+)/file/', views.image_file, name='cover_file'),
    url(r'^add_image/$', views.add_image, name='cover_add_image'),
]
