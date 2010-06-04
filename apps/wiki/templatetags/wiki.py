from __future__ import absolute_import

from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

from wiki.models import split_name

@register.filter
@stringfilter
def wiki_title(value):
    parts = (p.replace('_', ' ').title() for p in split_name(value))
    return ' / '.join(parts)
