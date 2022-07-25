# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('preview/', views.preview_from_xml, name='cover_preview'),
    path('preview/<slug:book>/', views.preview, name='cover_preview'),
    path('preview/<slug:book>/<slug:chunk>/',
            views.preview, name='cover_preview'),
    path('preview/<slug:book>/<slug:chunk>/<int:rev>/',
            views.preview, name='cover_preview'),

    path('image/', views.image_list, name='cover_image_list'),
    path('image/<int:pk>/', views.image, name='cover_image'),
    path('image/<int:pk>/file/', views.image_file, name='cover_file'),
    path('add_image/', views.add_image, name='cover_add_image'),
    path('quick-import/<int:pk>/', views.quick_import, name='cover_quick_import'),
]
