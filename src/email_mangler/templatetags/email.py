# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import codecs
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django import template

register = template.Library()


@register.filter
def email_link(email):
    email_safe = escape(email)
    try:
        name, domain = email_safe.split('@', 1)
    except ValueError:
        return email

    at = escape(_('at'))
    dot = escape(_('dot'))
    mangled = "%s %s %s" % (name, at, (' %s ' % dot).join(domain.split('.')))
    return mark_safe("<a class='mangled' data-addr1='%(name)s' "
        "data-addr2='%(domain)s'>%(mangled)s</a>" % {
            'name': codecs.encode(name, 'rot13'),
            'domain': codecs.encode(domain, 'rot13'),
            'mangled': mangled,
        })
