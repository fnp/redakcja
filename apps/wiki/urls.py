# -*- coding: utf-8
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.list_detail import object_detail
from django.conf import settings
from wiki.models import Book


#PART = ur"""[ ĄĆĘŁŃÓŚŻŹąćęłńóśżź0-9\w_.-]+"""

urlpatterns = patterns('wiki.views',
    url(r'^$', redirect_to, {'url': 'catalogue/'}),

    url(r'^catalogue/$', 'document_list', name='wiki_document_list'),
    #url(r'^catalogue/([^/]+)/$', 'document_list'),
    #url(r'^catalogue/([^/]+)/([^/]+)/$', 'document_list'),
    #url(r'^catalogue/([^/]+)/([^/]+)/([^/]+)$', 'document_list'),

    url(r'^edit/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor', name="wiki_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor_readonly', name="wiki_editor_readonly"),

    url(r'^upload/$',
        'upload', name='wiki_upload'),

    url(r'^create/(?P<slug>[^/]*)/',
        'create_missing', name='wiki_create_missing'),

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

    #url(r'^(?P<name>[^/]+)/publish$', 'publish', name="wiki_publish"),
    #url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$', 'publish', name="wiki_publish"),

    url(r'^diff/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$', 'diff', name="wiki_diff"),
    #url(r'^(?P<name>[^/]+)/tags$', 'add_tag', name="wiki_add_tag"),

    url(r'^full/(?P<slug>[^/]+)/$', 'compiled', name="wiki_compiled"),

    url(r'^book/(?P<slug>[^/]+)/$', object_detail, 
        {"queryset": Book.objects.all()}, name="wiki_book"),
)
