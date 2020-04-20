# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db.models import Prefetch
from django.views.generic import DetailView, TemplateView
from . import models
import documents.models


class CatalogueView(TemplateView):
    template_name = "catalogue/catalogue.html"

    def get_context_data(self):
        ctx = super().get_context_data()
        documents_books_queryset = models.Book.objects.prefetch_unrelated(
            "document_books", "slug", documents.models.Book, "dc_slug"
        )
        ctx["authors"] = models.Author.objects.all().prefetch_related(
            Prefetch("book_set", queryset=documents_books_queryset),
            Prefetch("translated_book_set", queryset=documents_books_queryset),
        )
        return ctx


class AuthorView(TemplateView):
    model = models.Author
    template_name = "catalogue/author_detail.html"

    def get_context_data(self, slug):
        ctx = super().get_context_data()
        documents_books_queryset = models.Book.objects.prefetch_unrelated(
            "document_books", "slug", documents.models.Book, "dc_slug"
        )
        authors = models.Author.objects.filter(slug=slug).prefetch_related(
            Prefetch("book_set", queryset=documents_books_queryset),
            Prefetch("translated_book_set", queryset=documents_books_queryset),
        )
        ctx["author"] = authors.first()
        return ctx


class BookView(DetailView):
    model = models.Book
