# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from toolbar import models

register = template.Library()


@register.inclusion_tag('toolbar/toolbar.html')
def toolbar():
    return {'toolbar_groups': models.ButtonGroup.objects.all().select_related()}


@register.inclusion_tag('toolbar/button.html')
def toolbar_button(b):
    return {'button': b}


@register.inclusion_tag('toolbar/keyboard.html')
def keyboard(groups):
    keys = {}
    for g in groups:
        for b in g.button_set.all():
            if b.accesskey:
                keys[b.accesskey] = b
    rows = [
        [
            {
                'symbol': symbol,
                'lower': keys.get(symbol.lower()),
                'upper': keys.get(symbol),
            }
            for symbol in row
        ]
        for row in ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
    ]

    return {'rows': rows}
