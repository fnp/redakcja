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
