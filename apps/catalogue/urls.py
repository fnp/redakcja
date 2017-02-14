# -*- coding: utf-8
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from catalogue.views import GalleryView

from catalogue import views

urlpatterns = (
    # url(r'^$', RedirectView.as_view(url='catalogue/')),

    url(r'^upcoming/$', views.upcoming, name='catalogue_upcoming'),
    url(r'^finished/$', views.finished, name='catalogue_finished'),

    url(r'^user/$', views.my, name='catalogue_user'),
    url(r'^user/(?P<username>[^/]+)/$', views.user, name='catalogue_user'),

    url(r'^create/',
        views.create_missing, name='catalogue_create_missing'),
    url(r'^fork/(?P<pk>\d+)/',
        views.fork, name='catalogue_fork'),

    url(r'^doc/(?P<pk>\d+)/publish$', views.publish, name="catalogue_publish"),
    url(r'^doc/(?P<pk>\d+)/unpublish$', views.unpublish, name="catalogue_unpublish"),

    url(r'^(?P<pk>[^/]+)/schedule/$', views.book_schedule, name="catalogue_book_schedule"),
    url(r'^(?P<pk>[^/]+)/owner/$', views.book_owner, name="catalogue_book_owner"),
    url(r'^(?P<pk>[^/]+)/delete/$', views.book_delete, name="catalogue_book_delete"),

    url(r'^(?P<pk>[^/]+)/attachments/$',
        login_required()(GalleryView.as_view()),
        name="catalogue_book_gallery"),
    url(r'^(?P<pk>\d+)/$', views.book_html, name="catalogue_html"),
    url(r'^(?P<pk>\d+)/preview/$', views.book_html, {'preview': True}, name="catalogue_preview"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/preview/$', views.book_html, {'preview': True}, name="catalogue_preview_rev"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/pdf/$', views.book_pdf, name="catalogue_pdf"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/epub/$', views.book_epub, name="catalogue_epub"),
    url(r'^(?P<pk>\d+)/rev(?P<rev_pk>\d+)/mobi/$', views.book_mobi, name="catalogue_mobi"),
)
