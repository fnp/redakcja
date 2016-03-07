# -*- coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import RedirectView
from catalogue.views import GalleryView, GalleryPackageView


urlpatterns = patterns('catalogue.views',
    #url(r'^$', RedirectView.as_view(url='catalogue/')),

    url(r'^upcoming/$', 'upcoming', name='catalogue_upcoming'),
    url(r'^finished/$', 'finished', name='catalogue_finished'),

    #url(r'^catalogue/$', 'document_list', name='catalogue_document_list'),
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
    url(r'^fork/(?P<pk>\d+)/',
        'fork', name='catalogue_fork'),

    url(r'^doc/(?P<pk>\d+)/publish$', 'publish', name="catalogue_publish"),
    url(r'^doc/(?P<pk>\d+)/unpublish$', 'unpublish', name="catalogue_unpublish"),
    #url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$', 'publish', name="catalogue_publish"),

    url(r'^(?P<pk>[^/]+)/schedule/$', 'book_schedule', name="catalogue_book_schedule"),
    url(r'^(?P<pk>[^/]+)/owner/$', 'book_owner', name="catalogue_book_owner"),
    url(r'^(?P<pk>[^/]+)/delete/$', 'book_delete', name="catalogue_book_delete"),

    url(r'^book/(?P<slug>[^/]+)/$', 'book', name="catalogue_book"),

    url(r'^(?P<pk>[^/]+)/attachments/$',
            login_required()(GalleryView.as_view()),
            name="catalogue_book_gallery"),
    #~ url(r'^attachments/$',
            #~ login_required()(GalleryView.as_view()),
            #~ name="catalogue_attachments"),
    #~ url(r'^attachments/(?P<pk>\d+)/$',
            #~ login_required()(GalleryView.as_view()),
            #~ name="catalogue_attachments"),
    url(r'^book/(?P<slug>[^/]+)/gallery/package$',
            permission_required('catalogue.change_book')(GalleryPackageView.as_view()),
            name="catalogue_book_gallery_package"),
    url(r'^book/(?P<slug>[^/]+)/xml$', 'book_xml', name="catalogue_book_xml"),
    #url(r'^book/(?P<slug>[^/]+)/txt$', 'book_txt', name="catalogue_book_txt"),
    url(r'^(?P<pk>\d+)/$', 'book_html', name="catalogue_html"),
    url(r'^(?P<pk>\d+)/preview/$', 'book_html', {'preview': True}, name="catalogue_preview"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/preview/$', 'book_html', {'preview': True}, name="catalogue_preview_rev"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/pdf/$', 'book_pdf', name="catalogue_pdf"),


    #url(r'^book/(?P<slug>[^/]+)/epub$', 'book_epub', name="catalogue_book_epub"),
    #url(r'^book/(?P<slug>[^/]+)/pdf$', 'book_pdf', name="catalogue_book_pdf"),

    url(r'^chunk_add/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        'chunk_add', name="catalogue_chunk_add"),
    url(r'^chunk_edit/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        'chunk_edit', name="catalogue_chunk_edit"),
    url(r'^book_append/(?P<slug>[^/]+)/$',
        'book_append', name="catalogue_book_append"),
    url(r'^chunk_mass_edit',
        'chunk_mass_edit', name='catalogue_chunk_mass_edit'),
)
