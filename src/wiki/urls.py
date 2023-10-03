# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('edit/<slug:slug>/<slug:chunk>/', views.editor, name="wiki_editor"),
    path('edit/<slug:slug>/', views.editor, name="wiki_editor"),

    path('readonly/<slug:slug>/<slug:chunk>/',
         views.editor_readonly, name="wiki_editor_readonly"),
    path('readonly/<slug:slug>/',
         views.editor_readonly, name="wiki_editor_readonly"),

    path('gallery/<directory>/', views.gallery, name="wiki_gallery"),
    path('scans/<int:pk>/', views.scans_list, name="wiki_scans"),
    path('history/<int:chunk_id>/', views.history, name="wiki_history"),
    path('rev/<int:chunk_id>/', views.revision, name="wiki_revision"),
    path('text/<int:chunk_id>/', views.text, name="wiki_text"),
    path('revert/<int:chunk_id>/', views.revert, name='wiki_revert'),
    path('diff/<int:chunk_id>/', views.diff, name="wiki_diff"),
    path('pubmark/<int:chunk_id>/', views.pubmark, name="wiki_pubmark"),
    path('galleries/', views.galleries),
    path('set-gallery/<int:chunk_id>/', views.set_gallery),
    path('set-gallery-start/<int:chunk_id>/', views.set_gallery_start),
    path('themes', views.themes, name="themes"),
    path('back/', views.back),
    path('editor-user-area/', views.editor_user_area),
]
