from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from documents.models import Book
from . import models


class SitePublishView(PermissionRequiredMixin, View):
    permission_required = 'depot.add_sitebookpublish'

    def post(self, request, site_id, book_id):
        site = get_object_or_404(models.Site, pk=site_id)
        book = get_object_or_404(Book, pk=book_id)
        try:
            publish = models.SiteBookPublish.create_for(book, request.user, site)
        except AssertionError:
            pass
        return redirect(book.get_absolute_url())
