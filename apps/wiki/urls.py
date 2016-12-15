# -*- coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'wiki.views',
    url(r'^edit/(?P<pk>[^/]+)/$',
        'editor', name="wiki_editor"),

    url(r'^gallery/(?P<directory>[^/]+)/$',
        'gallery', name="wiki_gallery"),

    url(r'^history/(?P<doc_id>\d+)/$',
        'history', name="wiki_history"),

    url(r'^text/(?P<doc_id>\d+)/$',
        'text', name="wiki_text"),

    url(r'^revert/(?P<doc_id>\d+)/$',
        'revert', name='wiki_revert'),

    url(r'^diff/(?P<doc_id>\d+)/$', 'diff', name="wiki_diff"),
)
