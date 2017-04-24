# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import django_filters
from django.utils.functional import lazy
from django_filters.filters import ModelMultipleChoiceFilter

from catalogue.models import Document, Category


def tag_filter(dc_tag):
    category = Category.objects.get(dc_tag=dc_tag)
    return ModelMultipleChoiceFilter(
        queryset=category.tag_set.all(), label=lazy(lambda: category.label, unicode)(), method='filter_by_tag')


class DocumentFilterSet(django_filters.FilterSet):
    language = tag_filter('language')
    license = tag_filter('rights')
    audience = tag_filter('audience')

    class Meta:
        model = Document
        fields = []

    def filter_by_tag(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(tags__in=value).distinct()
