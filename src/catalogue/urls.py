# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path("", views.CatalogueView.as_view(), name="catalogue"),
    path("author/<slug:slug>/", views.AuthorView.as_view(), name="catalogue_author"),
    path("book/<slug:slug>/", views.BookView.as_view(), name="catalogue_book"),
    path("book/<slug:slug>.json", views.BookAPIView.as_view(), name="catalogue_book_api"),

    path('terms/audience/', views.AudienceTerms.as_view()),
    path('terms/epoch/', views.EpochTerms.as_view()),
    path('terms/kind/', views.KindTerms.as_view()),
    path('terms/genre/', views.GenreTerms.as_view()),
    path('terms/wluri/', views.WLURITerms.as_view()),
    path('terms/book_title/', views.BookTitleTerms.as_view()),
    path('terms/author/', views.AuthorTerms.as_view()),
    path('terms/thema/', views.ThemaTerms.as_view()),
    path('terms/thema-main/', views.MainThemaTerms.as_view()),

    path('terms/editor/', views.EditorTerms.as_view()),

    path('chooser/thema/', views.ThemaChooser.as_view()),
    path('chooser/thema-main/', views.MainThemaChooser.as_view()),

    path('wikidata/<slug:model>/<qid>', views.WikidataView.as_view()),

    path('publish/author/<int:pk>/', views.publish_author, name='catalogue_publish_author'),
    path('publish/genre/<int:pk>/', views.publish_genre, name='catalogue_publish_genre'),
    path('publish/kind/<int:pk>/', views.publish_kind, name='catalogue_publish_kind'),
    path('publish/epoch/<int:pk>/', views.publish_epoch, name='catalogue_publish_epoch'),
    path('publish/collection/<int:pk>/', views.publish_collection, name='catalogue_publish_collection'),

    path('woblink/author/autocomplete', views.woblink_author_autocomplete,
         name='catalogue_woblink_author_autocomplete'),
]
