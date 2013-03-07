# -*- coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('wiki.views',
    url(r'^edit/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor', name="wiki_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor_readonly', name="wiki_editor_readonly"),

    url(r'^gallery/(?P<directory>[^/]+)/$',
        'gallery', name="wiki_gallery"),

    url(r'^history/(?P<chunk_id>\d+)/$',
        'history', name="wiki_history"),

    url(r'^rev/(?P<chunk_id>\d+)/$',
        'revision', name="wiki_revision"),

    url(r'^text/(?P<chunk_id>\d+)/$',
        'text', name="wiki_text"),

    url(r'^revert/(?P<chunk_id>\d+)/$',
        'revert', name='wiki_revert'),

    url(r'^diff/(?P<chunk_id>\d+)/$', 'diff', name="wiki_diff"),
    url(r'^pubmark/(?P<chunk_id>\d+)/$', 'pubmark', name="wiki_pubmark"),

    url(r'^themes$', 'themes', name="themes"),
)
