from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('wiki.views',
    url(r'^$',
        'document_list', name='wiki_doclist'),
    url(r'^create/(?P<name>[^/]+)',
        'document_create_missing', name='wiki_create_missing'),
    url(r'^gallery/(?P<directory>[^/]+)$',
        'document_gallery', name="wiki_gallery"),
    url(r'^(?P<name>[^/]+)/history$',
        'document_history', name="wiki_history"),
    url(r'^(?P<name>[^/]+)/text$',
        'document_text', name="wiki_text"),
    url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$',
        'document_publish', name="wiki_publish"),
    url(r'^(?P<name>[^/]+)/diff$',
        'document_diff', name="wiki_diff"),
    url(r'^(?P<name>[^/]+)/tags$',
        'document_add_tag', name="wiki_add_tag"),
    url(r'^(?P<name>[^/]+)/publish$', 'document_publish'),
    url(r'^(?P<name>[^/]+)$',
        'document_detail', name="wiki_details"),
)
