from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
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


@register.inclusion_tag("wiki/main_tabs.html", takes_context=True)
def main_tabs(context):
    active = getattr(context['request'], 'wiki_active_tab', None)

    tabs = []
    user = context['user']
    if user.is_authenticated():
        tabs.append(Tab('my', _('Assigned to me'), reverse("wiki_user")))

    tabs.append(Tab('unassigned', _('Unassigned'), reverse("wiki_unassigned")))
    tabs.append(Tab('users', _('Users'), reverse("wiki_users")))
    tabs.append(Tab('all', _('All'), reverse("wiki_document_list")))
    tabs.append(Tab('create', _('Add'), reverse("wiki_create_missing")))
    tabs.append(Tab('upload', _('Upload'), reverse("wiki_upload")))

    if user.is_staff:
        tabs.append(Tab('admin', _('Admin'), reverse("admin:index")))

    return {"tabs": tabs, "active_tab": active}
