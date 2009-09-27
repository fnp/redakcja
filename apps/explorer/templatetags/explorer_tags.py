from django import template
# from toolbar import models
register = template.Library()

from django.template.defaultfilters import stringfilter

@register.filter(name='bookname')
@stringfilter
def bookname(fileid):
    return ', '.join(\
            ' '.join(s.capitalize() for s in part.split('_'))\
        for part in fileid.split('$'))

@register.inclusion_tag('explorer/file_tree_part.html')
def tree_part(document):
    return {'document': document}