# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import apps
from django.db.models import Prefetch
from django.http import Http404
from django.utils.formats import localize_input
from django.contrib.auth.models import User
from django.views.generic import DetailView, TemplateView
from . import models
import documents.models
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers


class CatalogueView(TemplateView):
    template_name = "catalogue/catalogue.html"

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx["authors"] = models.Author.objects.all().prefetch_related('book_set__book_set', 'translated_book_set__book_set')

        return ctx


class AuthorView(TemplateView):
    model = models.Author
    template_name = "catalogue/author_detail.html"

    def get_context_data(self, slug):
        ctx = super().get_context_data()
        authors = models.Author.objects.filter(slug=slug).prefetch_related(
            Prefetch("book_set"),
            Prefetch("translated_book_set"),
        )
        ctx["author"] = authors.first()
        return ctx


class BookView(DetailView):
    model = models.Book


class TermSearchFilter(SearchFilter):
    search_param = 'term'


class Terms(ListAPIView):
    filter_backends = [TermSearchFilter]
    search_fields = ['name']

    class serializer_class(serializers.Serializer):
        label = serializers.CharField(source='name')


class EpochTerms(Terms):
    queryset = models.Epoch.objects.all()
class KindTerms(Terms):
    queryset = models.Kind.objects.all()
class GenreTerms(Terms):
    queryset = models.Genre.objects.all()

class AuthorTerms(Terms):
    search_fields = ['first_name', 'last_name']
    queryset = models.Author.objects.all()

class EditorTerms(Terms):
    search_fields = ['first_name', 'last_name', 'username']
    queryset = User.objects.all()

    class serializer_class(serializers.Serializer):
        label = serializers.SerializerMethodField()

        def get_label(self, obj):
            return f'{obj.last_name}, {obj.first_name}'
    
class BookTitleTerms(Terms):
    queryset = models.Book.objects.all()
    search_fields = ['title', 'slug']

    class serializer_class(serializers.Serializer):
        label = serializers.CharField(source='title')

class WLURITerms(Terms):
    queryset = models.Book.objects.all()
    search_fields = ['title', 'slug']
    
    class serializer_class(serializers.Serializer):
        label = serializers.CharField(source='wluri')


class WikidataView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, model, qid, save):
        try:
            Model = apps.get_model('catalogue', model)
        except LookupError:
            raise Http404
        if not issubclass(Model, models.WikidataModel):
            raise Http404

        obj = Model.objects.filter(wikidata=qid).first()
        if obj is None:
            obj = Model(wikidata=qid)
        if not obj.pk and save:
            obj.save()
        else:
            obj.wikidata_populate(save=False)
        d = {
            "id": obj.pk,
        }
        for attname in dir(Model.Wikidata):
            if attname.startswith("_"):
                continue
            for fieldname, lang in obj.wikidata_fields_for_attribute(attname):
                d[fieldname] = getattr(obj, fieldname)

                if isinstance(d[fieldname], models.WikidataModel):
                    d[attname] = {
                        "model": type(d[fieldname])._meta.model_name,
                        "wd": d[fieldname].wikidata,
                        "label": str(d[fieldname]) or d[fieldname]._wikidata_label,
                    }
                else:
                    d[fieldname] = localize_input(d[fieldname])
        return Response(d)
    
    def get(self, request, model, qid):
        return self.get_object(model, qid, save=False)

    def post(self, request, model, qid):
        return self.get_object(model, qid, save=True)
