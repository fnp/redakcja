# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from embeder import embed

register = template.Library()


@register.assignment_tag
def urlinfo(url):
    try:
        return embed.get(url).get('global', {})
    except:
        return {}
