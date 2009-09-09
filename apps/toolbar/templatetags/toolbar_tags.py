from django import template
# from toolbar import models

register = template.Library()

@register.inclusion_tag('toolbar/toolbar.html')
def toolbar(groups, extra):
    return {'toolbar_groups': groups, 'toolbar_extra_group': extra}

@register.inclusion_tag('toolbar/button.html')
def toolbar_button(b):
    return {'button': b}
