from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from documents.models import Book
from . import models


class LegimiPublishView(PermissionRequiredMixin, View):
    permission_required = 'depot.add_legimibookpublish'

    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        try:
            publish = models.LegimiBookPublish.create_for(book, request.user)
        except AssertionError:
            pass
        return redirect(book.get_absolute_url())
