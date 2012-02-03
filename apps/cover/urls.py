# -*- coding: utf-8
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('cover.views',
    url(r'^preview/$', 'preview_from_xml', name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/$', 'preview', name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/(?P<chunk>[^/]+)/$',
            'preview', name='cover_preview'),
    url(r'^preview/(?P<book>[^/]+)/(?P<chunk>[^/]+)/(?P<rev>\d+)/$',
            'preview', name='cover_preview'),
)
