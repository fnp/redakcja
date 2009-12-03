from django import template
from toolbar import models

register = template.Library()

@register.inclusion_tag('toolbar/toolbar.html')
def toolbar():
    return {'toolbar_groups': models.ButtonGroup.objects.all()}

@register.inclusion_tag('toolbar/button.html')
def toolbar_button(b):
    return {'button': b}
