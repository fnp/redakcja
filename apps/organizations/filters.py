# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import django_filters
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

from catalogue.filters import tag_filter
from organizations.models import Organization


class OrganizationFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains', label='',
        widget=TextInput(attrs={'placeholder': _('name')}))
    subject = tag_filter('subject')

    class Meta:
        model = Organization
        fields = []

    def filter_by_tag(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(document__tags__in=value).distinct()
