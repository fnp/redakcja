# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path, re_path
from django.contrib.auth.decorators import permission_required
from django.views.generic import RedirectView
from .feeds import PublishTrackFeed
from . import views


urlpatterns = [
    path('', RedirectView.as_view(url='catalogue/', permanent=False)),

    path('images/', views.image_list, name='documents_image_list'),
    path('image/<slug:slug>/', views.image, name="documents_image"),
    path('image/<slug:slug>/publish', views.publish_image,
            name="documents_publish_image"),

    path('catalogue/', views.document_list, name='documents_document_list'),
    path('user/', views.my, name='documents_user'),
    path('user/<username>/', views.user, name='documents_user'),
    path('users/', views.users, name='documents_users'),
    path('activity/', views.activity, name='documents_activity'),
    re_path(r'^activity/(?P<isodate>\d{4}-\d{2}-\d{2})/$', 
        views.activity, name='documents_activity'),

    path('upload/', views.upload, name='documents_upload'),

    path('create/<slug:slug>/',
        views.create_missing, name='documents_create_missing'),
    path('create/', views.create_missing, name='documents_create_missing'),

    path('book/<slug:slug>/publish', views.publish, name="documents_publish"),

    path('book/<slug:slug>/', views.book, name="documents_book"),
    path('book/<slug:slug>/gallery/',
            permission_required('documents.change_book')(views.GalleryView.as_view()),
            name="documents_book_gallery"),
    path('book/<slug:slug>/xml', views.book_xml, name="documents_book_xml"),
    path('book/dc/<slug:slug>/xml', views.book_xml_dc, name="documents_book_xml_dc"),
    path('book/<slug:slug>/txt', views.book_txt, name="documents_book_txt"),
    path('book/<slug:slug>/html', views.book_html, name="documents_book_html"),
    path('book/<slug:slug>/epub', views.book_epub, name="documents_book_epub"),
    path('book/<slug:slug>/epubcheck', views.book_epubcheck, name="documents_book_epubcheck"),
    path('book/<slug:slug>/mobi', views.book_mobi, name="documents_book_mobi"),
    path('book/<slug:slug>/pdf', views.book_pdf, name="documents_book_pdf"),
    path('book/<slug:slug>/pdf-mobile', views.book_pdf, kwargs={'mobile': True}, name="documents_book_pdf_mobile"),
    path('book/<slug:slug>/synchro', views.synchro, name="documents_book_synchro"),
    path('book/<int:pk>/attach/', views.attach_book_to_catalogue, name="documents_book_attach_to_catalogue"),

    path('chunk_add/<slug:slug>/<slug:chunk>/',
        views.chunk_add, name="documents_chunk_add"),
    path('chunk_edit/<slug:slug>/<slug:chunk>/',
        views.chunk_edit, name="documents_chunk_edit"),
    path('book_append/<slug:slug>/',
        views.book_append, name="documents_book_append"),
    path('chunk_mass_edit',
        views.chunk_mass_edit, name='documents_chunk_mass_edit'),
    path('image_mass_edit',
        views.image_mass_edit, name='documents_image_mass_edit'),

    path('track/<slug:slug>/', PublishTrackFeed()),
    path('active/', views.active_users_list, name='active_users_list'),
    path('active.csv', views.active_users_list, kwargs={'csv': True}, name='active_users_csv'),

    path('mark-final/', views.mark_final, name='mark_final'),
    path('mark-final-completed/', views.mark_final_completed, name='mark_final_completed'),
]
