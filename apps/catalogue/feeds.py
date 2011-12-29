# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from catalogue.models import Book, Chunk

class PublishTrackFeed(Feed):
    title = u"Planowane publikacje"
    link = "/"

    def description(self, obj):
        return u"Publikacje, które dotarły co najmniej do etapu: %s" % obj.name

    def get_object(self, request, slug):
        return get_object_or_404(Chunk.tag_model, slug=slug)

    def item_title(self, item):
        return item.title

    def items(self, obj):
        return Book.objects.filter(public=True, _on_track__gte=obj.ordering
                ).order_by('-_on_track', 'title')
