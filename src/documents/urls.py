# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from django.views.generic import RedirectView
from .feeds import PublishTrackFeed
from . import views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='catalogue/', permanent=False)),

    url(r'^images/$', views.image_list, name='documents_image_list'),
    url(r'^image/(?P<slug>[^/]+)/$', views.image, name="documents_image"),
    url(r'^image/(?P<slug>[^/]+)/publish$', views.publish_image,
            name="documents_publish_image"),

    url(r'^catalogue/$', views.document_list, name='documents_document_list'),
    url(r'^user/$', views.my, name='documents_user'),
    url(r'^user/(?P<username>[^/]+)/$', views.user, name='documents_user'),
    url(r'^users/$', views.users, name='documents_users'),
    url(r'^activity/$', views.activity, name='documents_activity'),
    url(r'^activity/(?P<isodate>\d{4}-\d{2}-\d{2})/$', 
        views.activity, name='documents_activity'),

    url(r'^upload/$',
        views.upload, name='documents_upload'),

    url(r'^create/(?P<slug>[^/]*)/',
        views.create_missing, name='documents_create_missing'),
    url(r'^create/',
        views.create_missing, name='documents_create_missing'),

    url(r'^book/(?P<slug>[^/]+)/publish$', views.publish, name="documents_publish"),

    url(r'^book/(?P<slug>[^/]+)/$', views.book, name="documents_book"),
    url(r'^book/(?P<slug>[^/]+)/gallery/$',
            permission_required('documents.change_book')(views.GalleryView.as_view()),
            name="documents_book_gallery"),
    url(r'^book/(?P<slug>[^/]+)/xml$', views.book_xml, name="documents_book_xml"),
    url(r'^book/dc/(?P<slug>[^/]+)/xml$', views.book_xml_dc, name="documents_book_xml_dc"),
    url(r'^book/(?P<slug>[^/]+)/txt$', views.book_txt, name="documents_book_txt"),
    url(r'^book/(?P<slug>[^/]+)/html$', views.book_html, name="documents_book_html"),
    url(r'^book/(?P<slug>[^/]+)/epub$', views.book_epub, name="documents_book_epub"),
    url(r'^book/(?P<slug>[^/]+)/mobi$', views.book_mobi, name="documents_book_mobi"),
    url(r'^book/(?P<slug>[^/]+)/pdf$', views.book_pdf, name="documents_book_pdf"),
    url(r'^book/(?P<slug>[^/]+)/pdf-mobile$', views.book_pdf, kwargs={'mobile': True}, name="documents_book_pdf_mobile"),

    url(r'^chunk_add/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        views.chunk_add, name="documents_chunk_add"),
    url(r'^chunk_edit/(?P<slug>[^/]+)/(?P<chunk>[^/]+)/$',
        views.chunk_edit, name="documents_chunk_edit"),
    url(r'^book_append/(?P<slug>[^/]+)/$',
        views.book_append, name="documents_book_append"),
    url(r'^chunk_mass_edit',
        views.chunk_mass_edit, name='documents_chunk_mass_edit'),
    url(r'^image_mass_edit',
        views.image_mass_edit, name='documents_image_mass_edit'),

    url(r'^track/(?P<slug>[^/]*)/$', PublishTrackFeed()),
    url(r'^active/$', views.active_users_list, name='active_users_list'),

    url(r'^mark-final/$', views.mark_final, name='mark_final'),
    url(r'^mark-final-completed/$', views.mark_final_completed, name='mark_final_completed'),
]
