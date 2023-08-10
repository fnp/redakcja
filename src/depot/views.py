from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from documents.models import Book
from . import models


class ShopPublishView(PermissionRequiredMixin, View):
    permission_required = 'depot.add_shopbookpublish'

    def post(self, request, shop_id, book_id):
        shop = get_object_or_404(models.Shop, pk=shop_id)
        book = get_object_or_404(Book, pk=book_id)
        try:
            publish = models.ShopBookPublish.create_for(book, request.user, shop)
        except AssertionError:
            pass
        return redirect(book.get_absolute_url())
