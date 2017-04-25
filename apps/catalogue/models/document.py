# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import unicode_literals

from datetime import date
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from dvcs.models import Ref
from organizations.models import Organization
from catalogue.constants import STAGES
from .tag import Tag, Category


def metadata_from_text(text):
    from lxml import etree
    metadata = {}
    text = text.replace(u'\ufeff', '')
    # This is bad. The editor shouldn't spew unknown HTML entities.
    text = text.replace(u'&nbsp;', u'\u00a0')

    try:
        t = etree.fromstring(text)
    except:
        return {'title': '<<Resource invalid>>'}
    header = t.find('.//header')
    if header is None:
        header = etree.fromstring(text).find('.//{http://nowoczesnapolska.org.pl/sst#}header')
    metadata['title'] = getattr(header, 'text', ' ') or ' '
    # print 'meta', d['title']

    m = t.find('metadata')
    if m is None:
        m = t.find('{http://nowoczesnapolska.org.pl/sst#}metadata')
    if m is not None:
        c = m.find('{http://purl.org/dc/elements/1.1/}relation.coverimage.url')
        if c is not None:
            metadata['cover_url'] = c.text
        for category in Category.objects.all():
            for elem in m.findall('{http://purl.org/dc/elements/1.1/}' + category.dc_tag):
                if elem.text is not None:
                    if category.multiple:
                        if category.dc_tag not in metadata:
                            metadata[category.dc_tag] = []
                        metadata[category.dc_tag].append(elem.text)
                    else:
                        if category.dc_tag in metadata:
                            metadata['multiple_values'] = category.dc_tag
                        metadata[category.dc_tag] = elem.text
    return metadata


class Document(Ref):
    """ An editable chunk of text."""

    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    owner_organization = models.ForeignKey(Organization, null=True)
    stage = models.CharField(_('stage'), max_length=128, blank=True, default=STAGES[0][0])
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='assignments')
    deleted = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    # we need to know if it were ever published (for notifications)
    published = models.BooleanField(default=False)

    # Where to cache searchable stuff from metadata?
    # Probably in some kind of search index.

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')

    def short_html(self):
        return render_to_string('catalogue/book_list/book.html', {'book': self})

    def meta(self):
        return metadata_from_text(self.materialize())

    def can_edit(self, user):
        if user.is_superuser:
            return True
        if self.owner_user:
            return self.owner_user == user
        else:
            return self.owner_organization.is_member(user)

    def set_stage(self, stage):
        self.stage = stage
        plan = self.get_plan()
        if plan is not None:
            self.assigned_to = plan.user
        else:
            self.assigned_to = None
        self.save()

    def stage_name(self):
        return force_unicode(dict(STAGES)[self.stage]) if self.stage else None

    def get_plan(self):
        try:
            plan = self.plan_set.get(stage=self.stage)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None
        return plan

    def is_overdue(self):
        plan = self.get_plan()
        return plan is not None and plan.deadline and plan.deadline < date.today()

    def commit(self, *args, **kwargs):
        super(Document, self).commit(*args, **kwargs)
        m = self.meta()
        for category in Category.objects.all():
            values = m.get(category.dc_tag)
            if not category.multiple:
                values = [values]
            if not values:
                values = []
            tags = category.tag_set.filter(dc_value__in=values)
            category.set_tags_for(self, tags)
