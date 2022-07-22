# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path("", views.CatalogueView.as_view(), name="catalogue"),
    path("author/<slug:slug>/", views.AuthorView.as_view(), name="catalogue_author"),
    path("book/<slug:slug>/", views.BookView.as_view(), name="catalogue_book"),

    path('terms/epoch/', views.EpochTerms.as_view()),
    path('terms/kind/', views.KindTerms.as_view()),
    path('terms/genre/', views.GenreTerms.as_view()),
    path('terms/wluri/', views.WLURITerms.as_view()),
    path('terms/book_title/', views.BookTitleTerms.as_view()),
    path('terms/author/', views.AuthorTerms.as_view()),

    path('terms/editor/', views.EditorTerms.as_view()),
]
