# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
register = template.Library()

@register.filter
def username(user):
    return ("%s %s" % (user.first_name, user.last_name)).lstrip() or user.username
