# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import reverse
from django import template
from django.utils.translation import ugettext as _

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
    user = context['user']
    tabs.append(Tab('my', _('My page'), reverse("catalogue_user")))

    tabs.append(Tab('activity', _('Activity'), reverse("catalogue_activity")))
    tabs.append(Tab('all', _('All'), reverse("catalogue_document_list")))
    tabs.append(Tab('images', _('Images'), reverse("catalogue_image_list")))
    tabs.append(Tab('users', _('Users'), reverse("catalogue_users")))

    if user.has_perm('catalogue.add_book'):
        tabs.append(Tab('create', _('Add'), reverse("catalogue_create_missing")))
        tabs.append(Tab('upload', _('Upload'), reverse("catalogue_upload")))

    tabs.append(Tab('cover', _('Covers'), reverse("cover_image_list")))

    return {"tabs": tabs, "active_tab": active}


@register.filter
def nice_name(user):
    return user.get_full_name() or user.username

