# -*- coding: utf-8
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from django.views.generic import RedirectView
from catalogue.feeds import PublishTrackFeed
from . import views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='catalogue/', permanent=False)),

    url(r'^images/$', views.image_list, name='catalogue_image_list'),
    url(r'^image/(?P<slug>[^/]+)/$', views.image, name="catalogue_image"),
    url(r'^image/(?P<slug>[^/]+)/publish$', views.publish_image,
            name="catalogue_publish_image"),

    url(r'^catalogue/$', views.document_list, name='catalogue_document_list'),
    url(r'^user/$', views.my, name='catalogue_user'),
    url(r'^user/(?P<username>[^/]+)/$', views.user, name='catalogue_user'),
    url(r'^users/$', views.users, name='catalogue_users'),
    url(r'^activity/$', views.activity, name='catalogue_activity'),
    url(r'^activity/(?P<isodate>\d{4}-\d{2}-\d{2})/$', 
        views.activity, name='catalogue_activity'),

    url(r'^upload/$',
        views.upload, name='catalogue_upload'),

    url(r'^create/(?P<slug>[^/]*)/',
        views.create_missing, name='catalogue_create_missing'),
    url(r'^create/',
        views.create_missing, name='catalogue_create_missing'),

    url(r'^book/(?P<slug>[^/]+)/publish$', views.publish, name="catalogue_publish"),

    url(r'^book/(?P<slug>[^/]+)/$', views.book, name="catalogue_book"),
    url(r'^book/(?P<slug>[^/]+)/gallery/$',
            permission_required('catalogue.change_book')(views.GalleryView.as_view()),
            name="catalogue_book_gallery"),
    url(r'^book/(?P<slug>[^/]+)/xml$', views.book_xml, name="catalogue_book_xml"),
    url(r'^book/dc/(?P<slug>[^/]+)/xml$', views.book_xml_dc, name="catalogue_book_xml_dc"),
    url(r'^book/(?P<slug>[^/]+)/txt$', views.book_txt, name="catalogue_book_txt"),
    url(r'^book/(?P<slug>[^/]+)/html$', views.book_html, name="catalogue_book_html"),
    url(r'^book/(?P<slug>[^/]+)/epub$', views.book_epub, name="catalogue_book_epub"),
    url(r'^book/(?P<slug>[^/]+)/mobi$', views.book_mobi, name="catalogue_book_mobi"),
    url(r'^book/(?P<slug>[^/]+)/pdf$', views.book_pdf, name="catalogue_book_pdf"),
    url(r'^book/(?P<slug>[^/]+)/pdf-mobile$', views.book_pdf, kwargs={'mobile': True}, name="catalogue_book_pdf_mobile"),

    url(r'^chunk_add/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        views.chunk_add, name="catalogue_chunk_add"),
    url(r'^chunk_edit/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        views.chunk_edit, name="catalogue_chunk_edit"),
    url(r'^book_append/(?P<slug>[^/]+)/$',
        views.book_append, name="catalogue_book_append"),
    url(r'^chunk_mass_edit',
        views.chunk_mass_edit, name='catalogue_chunk_mass_edit'),
    url(r'^image_mass_edit',
        views.image_mass_edit, name='catalogue_image_mass_edit'),

    url(r'^track/(?P<slug>[^/]*)/$', PublishTrackFeed()),
    url(r'^active/$', views.active_users_list, name='active_users_list'),

    url(r'^mark-final/$', views.mark_final, name='mark_final'),
    url(r'^mark-final-completed/$', views.mark_final_completed, name='mark_final_completed'),
]
