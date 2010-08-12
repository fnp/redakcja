# -*- coding: utf-8
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings


PART = ur"""[ ĄĆĘŁŃÓŚŻŹąćęłńóśżź0-9\w_.-]+"""

urlpatterns = patterns('wiki.views',
    url(r'^$', redirect_to, {'url': 'catalogue/'}),

    url(r'^catalogue/$', 'document_list', name='wiki_document_list'),
    url(r'^catalogue/([^/]+)/$', 'document_list'),
    url(r'^catalogue/([^/]+)/([^/]+)/$', 'document_list'),
    url(r'^catalogue/([^/]+)/([^/]+)/([^/]+)$', 'document_list'),

    url(r'^(?P<name>%s)$' % PART,
        'editor', name="wiki_editor"),

    url(r'^(?P<name>[^/]+)/readonly$',
        'editor_readonly', name="wiki_editor_readonly"),

    url(r'^upload/$',
        'upload', name='wiki_upload'),

    url(r'^create/(?P<name>[^/]+)',
        'create_missing', name='wiki_create_missing'),

    url(r'^(?P<directory>[^/]+)/gallery$',
        'gallery', name="wiki_gallery"),

    url(r'^(?P<name>[^/]+)/history$',
        'history', name="wiki_history"),

    url(r'^(?P<name>[^/]+)/text$',
        'text', name="wiki_text"),

    url(r'^(?P<name>[^/]+)/publish$', 'publish', name="wiki_publish"),
    url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$', 'publish', name="wiki_publish"),

    url(r'^(?P<name>[^/]+)/diff$', 'diff', name="wiki_diff"),
    url(r'^(?P<name>[^/]+)/tags$', 'add_tag', name="wiki_add_tag"),



)
