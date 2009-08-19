from django import template

from toolbar import models


register = template.Library()


@register.inclusion_tag('toolbar/toolbar.html')
def toolbar():
    groups = models.ButtonGroup.objects.all()
    return {'groups': groups}

