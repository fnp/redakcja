# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^edit/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        views.editor, name="wiki_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        views.editor_readonly, name="wiki_editor_readonly"),

    url(r'^gallery/(?P<directory>[^/]+)/$',
        views.gallery, name="wiki_gallery"),

    url(r'^history/(?P<chunk_id>\d+)/$',
        views.history, name="wiki_history"),

    url(r'^rev/(?P<chunk_id>\d+)/$',
        views.revision, name="wiki_revision"),

    url(r'^text/(?P<chunk_id>\d+)/$',
        views.text, name="wiki_text"),

    url(r'^revert/(?P<chunk_id>\d+)/$',
        views.revert, name='wiki_revert'),

    url(r'^diff/(?P<chunk_id>\d+)/$', views.diff, name="wiki_diff"),
    url(r'^pubmark/(?P<chunk_id>\d+)/$', views.pubmark, name="wiki_pubmark"),

    url(r'^themes$', views.themes, name="themes"),
]
