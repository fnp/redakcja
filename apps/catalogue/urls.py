# -*- coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.views.generic import RedirectView
from catalogue.feeds import PublishTrackFeed
from catalogue.views import GalleryView, GalleryPackageView


urlpatterns = patterns('catalogue.views',
    url(r'^$', RedirectView.as_view(url='catalogue/')),

    url(r'^catalogue/$', 'document_list', name='catalogue_document_list'),
    url(r'^user/$', 'my', name='catalogue_user'),
    url(r'^user/(?P<username>[^/]+)/$', 'user', name='catalogue_user'),
    url(r'^users/$', 'users', name='catalogue_users'),
    url(r'^activity/$', 'activity', name='catalogue_activity'),
    url(r'^activity/(?P<isodate>\d{4}-\d{2}-\d{2})/$', 
        'activity', name='catalogue_activity'),

    url(r'^upload/$',
        'upload', name='catalogue_upload'),

    url(r'^create/(?P<slug>[^/]*)/',
        'create_missing', name='catalogue_create_missing'),
    url(r'^create/',
        'create_missing', name='catalogue_create_missing'),

    url(r'^book/(?P<slug>[^/]+)/publish$', 'publish', name="catalogue_publish"),
    #url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$', 'publish', name="catalogue_publish"),

    url(r'^book/(?P<slug>[^/]+)/$', 'book', name="catalogue_book"),
    url(r'^book/(?P<slug>[^/]+)/gallery/$',
            permission_required('catalogue.change_book')(GalleryView.as_view()),
            name="catalogue_book_gallery"),
    url(r'^book/(?P<slug>[^/]+)/gallery/package$',
            permission_required('catalogue.change_book')(GalleryPackageView.as_view()),
            name="catalogue_book_gallery_package"),
    url(r'^book/(?P<slug>[^/]+)/xml$', 'book_xml', name="catalogue_book_xml"),
    url(r'^book/(?P<slug>[^/]+)/txt$', 'book_txt', name="catalogue_book_txt"),
    url(r'^book/(?P<slug>[^/]+)/html$', 'book_html', name="catalogue_book_html"),
    url(r'^book/(?P<slug>[^/]+)/epub$', 'book_epub', name="catalogue_book_epub"),
    url(r'^book/(?P<slug>[^/]+)/pdf$', 'book_pdf', name="catalogue_book_pdf"),

    url(r'^chunk_add/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        'chunk_add', name="catalogue_chunk_add"),
    url(r'^chunk_edit/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        'chunk_edit', name="catalogue_chunk_edit"),
    url(r'^book_append/(?P<slug>[^/]+)/$',
        'book_append', name="catalogue_book_append"),
    url(r'^chunk_mass_edit',
        'chunk_mass_edit', name='catalogue_chunk_mass_edit'),

    url(r'^track/(?P<slug>[^/]*)/$', PublishTrackFeed()),
)
