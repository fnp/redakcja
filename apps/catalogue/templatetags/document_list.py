# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import absolute_import

from django.db.models import Q
from django import template
from django.utils.translation import ugettext_lazy as _
from catalogue.models import Document

register = template.Library()


_states = [
        ('publishable', _('publishable'), Q(book___new_publishable=True)),
        ('changed', _('changed'), Q(_changed=True)),
        ('published', _('published'), Q(book___published=True)),
        ('unpublished', _('unpublished'), Q(book___published=False)),
        ('empty', _('empty'), Q(head=None)),
    ]
_states_options = [s[:2] for s in _states]
_states_dict = dict([(s[0], s[2]) for s in _states])


@register.inclusion_tag('catalogue/book_list/book_list.html', takes_context=True)
def document_list(context, user=None, organization=None):
    request = context['request']

    # if user:
    #     filters = {"user": user}
    #     new_context = {"viewed_user": user}
    # else:
    #     filters = {}
    #     new_context = {
    #         "users": User.objects.annotate(
    #             count=Count('chunk')).filter(count__gt=0).order_by(
    #             '-count', 'last_name', 'first_name'),
    #         "other_users": User.objects.annotate(
    #             count=Count('chunk')).filter(count=0).order_by(
    #             'last_name', 'first_name'),
    #             }

    docs = Document.objects.filter(deleted=False)
    if user is not None:
        docs = docs.filter(
            Q(owner_user=user) | Q(owner_organization__membership__user=user) | Q(assigned_to=user)).distinct()
    if organization is not None:
        docs = docs.filter(owner_organization=organization)

    new_context = {}
    new_context.update({
        # "filters": True,
        "request": request,
        "books": docs,
        # "stages": Chunk.tag_model.objects.all(),
        # "states": _states_options,
    })

    return new_context


@register.inclusion_tag('catalogue/book_list/book.html', takes_context=True)
def document_short_html(context, doc):
    user = context['request'].user
    return {
        'am_owner':doc.can_edit(user),
        'book': doc,
    }
