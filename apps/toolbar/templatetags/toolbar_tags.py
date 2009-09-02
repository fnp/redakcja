from django import template
from toolbar import models

register = template.Library()

@register.inclusion_tag('toolbar/toolbar.html')
def toolbar():
    groups = models.ButtonGroup.objects.all()
    return {'groups': groups}

@register.filter
def keycode(value):
    return ord(str(value).upper())

