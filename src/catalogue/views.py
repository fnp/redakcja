# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import apps
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.utils.formats import localize_input
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView
import apiclient
from . import models
import documents.models
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from depot.woblink import get_woblink_session




class CatalogueView(TemplateView):
    template_name = "catalogue/catalogue.html"

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx["authors"] = models.Author.objects.all().prefetch_related('book_set__document_books', 'translated_book_set__document_books')

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

class BookAPIView(RetrieveAPIView):
    queryset = models.Book.objects.all()
    lookup_field = 'slug'

    class serializer_class(serializers.ModelSerializer):
        class AuthorSerializer(serializers.ModelSerializer):
            literal = serializers.CharField(source='name')

            class Meta:
                model = models.Author
                fields = ['literal']

        def category_serializer(m):
            class CategorySerializer(serializers.ModelSerializer):
                literal = serializers.CharField(source='name')
                class Meta:
                    model = m
                    fields = ['literal']
            return CategorySerializer

        authors = AuthorSerializer(many=True)
        translators = AuthorSerializer(many=True)
        epochs = category_serializer(models.Epoch)(many=True)
        kinds = category_serializer(models.Kind)(many=True)
        genres = category_serializer(models.Genre)(many=True)

        class Meta:
            model = models.Book
            fields = [
                'title',
                'authors',
                'translators',
                'epochs',
                'kinds',
                'genres',
                'scans_source',
                'text_source',
                'original_year',
                'pd_year',
            ]


class TermSearchFilter(SearchFilter):
    search_param = 'term'


class Terms(ListAPIView):
    filter_backends = [TermSearchFilter]
    search_fields = ['name']

    class serializer_class(serializers.Serializer):
        label = serializers.CharField(source='name')


class AudienceTerms(Terms):
    queryset = models.Audience.objects.all()
    search_fields = ['code', 'name', 'description']

    class serializer_class(serializers.Serializer):
        label = serializers.CharField(source='code')
        name = serializers.CharField()
        description = serializers.CharField()

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

class ThemaTerms(Terms):
    queryset = models.Thema.objects.filter(usable=True, hidden=False)
    search_fields = ['code', 'name', 'description']

    class serializer_class(serializers.Serializer):
        label = serializers.CharField(source='code')
        name = serializers.CharField()
        description = serializers.CharField()

class MainThemaTerms(ThemaTerms):
    queryset = models.Thema.objects.filter(usable=True, hidden=False, usable_as_main=True)



class Chooser(APIView):
    def get(self, request):
        return Response([{
            'value': 'x',
            'name': 'name',
            'description': 'desc',
            'sub': [
                {
                    'value': 'y',
                    'name': 'name y',
                    'description': 'desc y',
                }
            ]
        }])


class ThemaChooser(Chooser):
    queryset = models.Thema.objects.filter(usable=True, hidden=False)

    def get(self, request):
        tree = {}

        def getitem(code):
            if len(code) == 1:
                parent = tree
            else:
                parent = getitem(code[:-1]).setdefault('sub', {})
            return parent.setdefault(code, {})

        def getmissing(t):
            for k, v in t.items():
                if 'name' not in v:
                    yield k
                if 'sub' in v:
                    for c in getmissing(v['sub']):
                        yield c

        def populate(thema):
            item = getitem(thema.code)
            item['usable'] = thema.usable
            item['hidden'] = thema.hidden
            item['name'] = thema.name
            item['description'] = thema.description

        def order(tree):
            res = []
            for k, v in tree.items():
                v.update(value=k)
                if 'sub' in v:
                    v['sub'] = order(v['sub'])
                res.append(v)
            while len(res) == 1 and 'name' not in res[0] and 'sub' in res[0]:
                res = res[0]['sub']
            return res

        for thema in self.queryset.all():
            populate(thema)

        missing = list(getmissing(tree))
        for thema in models.Thema.objects.filter(code__in=missing):
            populate(thema)

        tree = order(tree)

        return Response(tree)


class MainThemaChooser(ThemaChooser):
    queryset = models.Thema.objects.filter(usable=True, hidden=False, usable_as_main=True)[:1000]


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
            obj.wikidata_populate(save=False, force=True)
        d = {
            "id": obj.pk,
            "__str__": str(obj),
        }
        for attname in dir(Model.Wikidata):
            if attname.startswith("_"):
                continue
            for fieldname, lang in obj.wikidata_fields_for_attribute(attname):
                try:
                    d[fieldname] = getattr(obj, fieldname)
                except ValueError:
                    # Like accessing related field on non-saved object.
                    continue

                if isinstance(d[fieldname], models.WikidataModel):
                    d[fieldname] = {
                        "model": type(d[fieldname])._meta.model_name,
                        "id": d[fieldname].pk,
                        "wd": d[fieldname].wikidata,
                        "label": str(d[fieldname]) or d[fieldname]._wikidata_label,
                    }
                elif hasattr(d[fieldname], 'all'):
                    d[fieldname] = [
                        {
                            "model": type(item)._meta.model_name,
                            "id": item.pk,
                            "wd": item.wikidata,
                            "label": str(item) or item._wikidata_label
                        } for item in d[fieldname].all()
                    ]
                elif hasattr(d[fieldname], 'as_hint_json'):
                    d[fieldname] = d[fieldname].as_hint_json()
                elif hasattr(d[fieldname], 'storage'):
                    d[fieldname] = d[fieldname].url if d[fieldname] else None
                else:
                    d[fieldname] = localize_input(d[fieldname])
        return Response(d)

    def get(self, request, model, qid):
        return self.get_object(model, qid, save=False)

    def post(self, request, model, qid):
        return self.get_object(model, qid, save=True)


@require_POST
@login_required
def publish_author(request, pk):
    author = get_object_or_404(models.Author, pk=pk)
    data = {
        "name_pl": author.name,
        "description_pl": author.generate_description(),
        "genitive": author.genitive,
        "gazeta_link": author.gazeta_link,
        "culturepl_link": author.culturepl_link,
        "wiki_link_pl": author.plwiki,
        "photo": request.build_absolute_uri(author.photo.url) if author.photo else None,
        "photo_source": author.photo_source,
        "photo_attribution": author.photo_attribution,
    }
    apiclient.api_call(request.user, f"authors/{author.slug}/", data)
    return redirect(reverse('admin:catalogue_author_change', args=[author.pk]))


@require_POST
@login_required
def publish_genre(request, pk):
    obj = get_object_or_404(models.Genre, pk=pk)
    data = {
        "name_pl": obj.name,
        "description_pl": obj.description,
        "plural": obj.plural,
        "is_epoch_specific": obj.is_epoch_specific,
    }
    apiclient.api_call(request.user, f"genres/{obj.slug}/", data)
    return redirect(reverse('admin:catalogue_genre_change', args=[obj.pk]))


@require_POST
@login_required
def publish_kind(request, pk):
    obj = get_object_or_404(models.Kind, pk=pk)
    data = {
        "name_pl": obj.name,
        "description_pl": obj.description,
        "collective_noun": obj.collective_noun,
    }
    apiclient.api_call(request.user, f"kinds/{obj.slug}/", data)
    return redirect(reverse('admin:catalogue_kind_change', args=[obj.pk]))


@require_POST
@login_required
def publish_epoch(request, pk):
    obj = get_object_or_404(models.Epoch, pk=pk)
    data = {
        "name_pl": obj.name,
        "description_pl": obj.description,
        "adjective_feminine_singular": obj.adjective_feminine_singular,
        "adjective_nonmasculine_plural": obj.adjective_feminine_singular,
    }
    apiclient.api_call(request.user, f"epochs/{obj.slug}/", data)
    return redirect(reverse('admin:catalogue_epoch_change', args=[obj.pk]))


@require_POST
@login_required
def publish_collection(request, pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    data = {
        "title": collection.name,
        "description": collection.description,
        "book_slugs": "\n".join(
            book.slug
            for book in collection.book_set.exclude(slug=None).exclude(slug='')
        )
    }
    apiclient.api_call(
        request.user,
        f"collections/{collection.slug}/",
        data,
        method='PUT',
        as_json=True,
    )
    return redirect(reverse(
        'admin:catalogue_collection_change', args=[collection.pk]
    ))


@login_required
def woblink_author_autocomplete(request):
    session = get_woblink_session()
    term = request.GET.get('term')
    if not term:
        return JsonResponse({})
    response = session.get(
        'https://publisher.woblink.com/author/autocomplete/' + term
    ).json()
    return JsonResponse({
        "results": [
            {
                "id": item['autId'],
                "text": item['autFullname'],
            }
            for item in response
        ],
    })
