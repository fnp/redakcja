# -*- coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from catalogue.views import GalleryView


urlpatterns = patterns(
    'catalogue.views',
    # url(r'^$', RedirectView.as_view(url='catalogue/')),

    url(r'^upcoming/$', 'upcoming', name='catalogue_upcoming'),
    url(r'^finished/$', 'finished', name='catalogue_finished'),

    url(r'^user/$', 'my', name='catalogue_user'),
    url(r'^user/(?P<username>[^/]+)/$', 'user', name='catalogue_user'),

    url(r'^create/(?P<slug>[^/]*)/',
        'create_missing', name='catalogue_create_missing'),
    url(r'^create/',
        'create_missing', name='catalogue_create_missing'),
    url(r'^fork/(?P<pk>\d+)/',
        'fork', name='catalogue_fork'),

    url(r'^doc/(?P<pk>\d+)/publish$', 'publish', name="catalogue_publish"),
    url(r'^doc/(?P<pk>\d+)/unpublish$', 'unpublish', name="catalogue_unpublish"),

    url(r'^(?P<pk>[^/]+)/schedule/$', 'book_schedule', name="catalogue_book_schedule"),
    url(r'^(?P<pk>[^/]+)/owner/$', 'book_owner', name="catalogue_book_owner"),
    url(r'^(?P<pk>[^/]+)/delete/$', 'book_delete', name="catalogue_book_delete"),

    url(r'^(?P<pk>[^/]+)/attachments/$',
        login_required()(GalleryView.as_view()),
        name="catalogue_book_gallery"),
    url(r'^(?P<pk>\d+)/$', 'book_html', name="catalogue_html"),
    url(r'^(?P<pk>\d+)/preview/$', 'book_html', {'preview': True}, name="catalogue_preview"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/preview/$', 'book_html', {'preview': True}, name="catalogue_preview_rev"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/pdf/$', 'book_pdf', name="catalogue_pdf"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/epub/$', 'book_epub', name="catalogue_epub"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/mobi/$', 'book_mobi', name="catalogue_mobi"),
)
