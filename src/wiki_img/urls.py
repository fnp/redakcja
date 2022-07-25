# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('edit/<slug:slug>/',
        views.editor, name="wiki_img_editor"),

    path('readonly/<slug:slug>/',
        views.editor_readonly, name="wiki_img_editor_readonly"),

    path('text/<int:image_id>/',
        views.text, name="wiki_img_text"),

    path('history/<int:object_id>/',
        views.history, name="wiki_img_history"),

    path('revert/<int:object_id>/',
        views.revert, name='wiki_img_revert'),

    path('diff/<int:object_id>/', views.diff, name="wiki_img_diff"),
    path('pubmark/<int:object_id>/', views.pubmark, name="wiki_img_pubmark"),
]
