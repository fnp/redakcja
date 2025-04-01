from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import Http404
from .. import models
from . import serializers


class BookList(ListAPIView):
    serializer_class = serializers.BookSerializer
    search_fields = ['title']

    def get_queryset(self):
        return models.Book.get_visible_for(self.request.user)


class BookDetail(RetrieveAPIView):
    serializer_class = serializers.BookDetailSerializer

    def get_queryset(self):
        return models.Book.get_visible_for(self.request.user)
    

class ChunkList(ListAPIView):
    queryset = models.Chunk.objects.all()
    serializer_class = serializers.ChunkSerializer
    filterset_fields = ['user', 'stage']
    search_fields = [
        'book__title',
        '=book_slug',
    ]

    def get_queryset(self):
        return models.Chunk.get_visible_for(self.request.user)


class ChunkDetail(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.ChunkDetailSerializer

    def get_queryset(self):
        return models.Chunk.get_visible_for(self.request.user)


class ChunkRevisionList(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.RevisionSerializer
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.RevisionDetailSerializer
        else:
            return serializers.RevisionSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        try:
            ctx["chunk"] = models.Chunk.objects.get(pk=self.kwargs['pk'])
        except models.Chunk.DoesNotExist:
            raise Http404
        return ctx

    def get_queryset(self):
        try:
            return models.Chunk.get_visible_for(self.request.user).get(
                pk=self.kwargs['pk']
            ).change_set.all()
        except models.Chunk.DoesNotExist:
            raise Http404()


class RevisionDetail(RetrieveAPIView):
    queryset = models.Chunk.change_model.objects.all()
    serializer_class = serializers.RevisionDetailSerializer

    def get_queryset(self):
        return models.Chunk.get_revisions_visible_for(self.request.user)

