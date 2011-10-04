# -*- coding: utf-8
from django.conf.urls.defaults import *


urlpatterns = patterns('wiki.views',
    url(r'^edit/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor', name="wiki_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor_readonly', name="wiki_editor_readonly"),

    url(r'^gallery/(?P<directory>[^/]+)/$',
        'gallery', name="wiki_gallery"),

    url(r'^history/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'history', name="wiki_history"),

    url(r'^rev/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'revision', name="wiki_revision"),

    url(r'^text/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'text', name="wiki_text"),

    url(r'^revert/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'revert', name='wiki_revert'),

    url(r'^diff/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$', 'diff', name="wiki_diff"),
    url(r'^pubmark/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$', 'pubmark', name="wiki_pubmark"),

    url(r'^themes$', 'themes', name="themes"),
)
