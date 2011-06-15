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
    url(r'^unassigned/$', 'unassigned', name='wiki_unassigned'),
    url(r'^user/$', 'my', name='wiki_user'),
    url(r'^user/(?P<username>[^/]+)/$', 'user', name='wiki_user'),

    url(r'^edit/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor', name="wiki_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$',
        'editor_readonly', name="wiki_editor_readonly"),

    url(r'^upload/$',
        'upload', name='wiki_upload'),

    url(r'^create/(?P<slug>[^/]*)/',
        'create_missing', name='wiki_create_missing'),
    url(r'^create/',
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

    url(r'^book/(?P<slug>[^/]+)/publish$', 'publish', name="wiki_publish"),
    #url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$', 'publish', name="wiki_publish"),

    url(r'^diff/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$', 'diff', name="wiki_diff"),
    url(r'^tag/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$', 'add_tag', name="wiki_add_tag"),
    url(r'^pubmark/(?P<slug>[^/]+)/(?:(?P<chunk>[^/]+)/)?$', 'pubmark', name="wiki_pubmark"),

    url(r'^book/(?P<slug>[^/]+)/$', 'book', name="wiki_book"),
    url(r'^book/(?P<slug>[^/]+)/xml$', 'book_xml', name="wiki_book_xml"),
    url(r'^book/(?P<slug>[^/]+)/txt$', 'book_txt', name="wiki_book_txt"),
    url(r'^book/(?P<slug>[^/]+)/html$', 'book_html', name="wiki_book_html"),
    #url(r'^book/(?P<slug>[^/]+)/epub$', 'book_epub', name="wiki_book_epub"),
    #url(r'^book/(?P<slug>[^/]+)/pdf$', 'book_pdf', name="wiki_book_pdf"),
    url(r'^chunk_add/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        'chunk_add', name="wiki_chunk_add"),
    url(r'^chunk_edit/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        'chunk_edit', name="wiki_chunk_edit"),
    url(r'^book_append/(?P<slug>[^/]+)/$',
        'book_append', name="wiki_book_append"),
    url(r'^book_edit/(?P<slug>[^/]+)/$',
        'book_edit', name="wiki_book_edit"),

)
