# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from catalogue.models import Book, Chunk

class PublishTrackFeed(Feed):
    title = u"Planowane publikacje"
    link = "/"

    def description(self, obj):
        tag, published = obj
        return u"Publikacje, które dotarły co najmniej do etapu: %s" % tag.name

    def get_object(self, request, slug):
        published = request.GET.get('published')
        if published is not None:
            published = published == 'true'
        return get_object_or_404(Chunk.tag_model, slug=slug), published

    def item_title(self, item):
        return item.title

    def items(self, obj):
        tag, published = obj
        books = Book.objects.filter(public=True, _on_track__gte=tag.ordering
                ).order_by('-_on_track', 'title')
        if published is not None:
            books = books.filter(_published=published)
        return books
