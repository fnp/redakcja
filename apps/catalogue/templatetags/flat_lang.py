# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import translation

from django import template

register = template.Library()


@register.assignment_tag
def flat_lang(page):
    try:
        return type(page).objects.get(url="%s%s/" % (page.url, translation.get_language()))
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return page
