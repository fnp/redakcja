# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path("", views.CatalogueView.as_view(), name="catalogue"),
    path("author/<slug:slug>/", views.AuthorView.as_view(), name="catalogue_author"),
    path("book/<slug:slug>/", views.BookView.as_view(), name="catalogue_book"),
]
