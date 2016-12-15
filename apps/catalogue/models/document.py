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
from django.utils.translation import ugettext_lazy as _
from dvcs.models import Ref
from organizations.models import Organization
from catalogue.constants import STAGES
from .tag import Tag


class Document(Ref):
    """ An editable chunk of text."""

    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    owner_organization = models.ForeignKey(Organization, null=True)
    stage = models.CharField(_('stage'), max_length=128, blank=True, default=STAGES[0])
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='assignments')
    deleted = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)

    # Where to cache searchable stuff from metadata?
    # Probably in some kind of search index.

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')

    def short_html(self):
        return render_to_string('catalogue/book_list/book.html', {'book': self})

    def meta(self):
        from lxml import etree
        metadata = {}

        data = self.materialize()
        data = data.replace(u'\ufeff', '')
        # This is bad. The editor shouldn't spew unknown HTML entities.
        data = data.replace(u'&nbsp;', u'\u00a0')

        try:
            t = etree.fromstring(data)
        except:
            return {'title': '<<Resource invalid>>'}
        header = t.find('.//header')
        if header is None:
            header = etree.fromstring(data).find('.//{http://nowoczesnapolska.org.pl/sst#}header')
        metadata['title'] = getattr(header, 'text', ' ') or ' '
        # print 'meta', d['title']

        m = t.find('metadata')
        if m is None:
            m = t.find('{http://nowoczesnapolska.org.pl/sst#}metadata')
        if m is not None:
            c = m.find('{http://purl.org/dc/elements/1.1/}relation.coverimage.url')
            if c is not None:
                metadata['cover_url'] = c.text
            c = m.find('{http://purl.org/dc/elements/1.1/}audience')
            if c is not None:
                metadata['audience'] = c.text

        return metadata

    def can_edit(self, user):
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

    def get_plan(self):
        try:
            plan = self.plan_set.get(stage=self.stage)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None
        return plan

    def is_overdue(self):
        plan = self.get_plan()
        return plan is not None and plan.deadline and plan.deadline < date.today()
