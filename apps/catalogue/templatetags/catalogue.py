# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import absolute_import

from django import template

register = template.Library()


class Tab(object):
    slug = None
    caption = None
    url = None

    def __init__(self, slug, caption, url):
        self.slug = slug
        self.caption = caption
        self.url = url


@register.inclusion_tag("catalogue/main_tabs.html", takes_context=True)
def main_tabs(context):
    active = getattr(context['request'], 'catalogue_active_tab', None)

    tabs = []
    # tabs.append(Tab('my', _('My page'), reverse("catalogue_user")))
    #
    # tabs.append(Tab('all', _('All'), reverse("catalogue_document_list")))

    return {"tabs": tabs, "active_tab": active}


@register.filter
def nice_name(user):
    return user.get_full_name() or user.username
