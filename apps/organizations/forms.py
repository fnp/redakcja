# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.contrib.sites.models import Site

from redakcja.utlis import send_notify_email
from .models import Organization, UserCard, countries


class OrganizationForm(forms.ModelForm):
    cts = countries

    class Meta:
        model = Organization
        exclude = ['_html']

    def save(self, commit=True):
        new = self.instance.id is None
        organization = super(OrganizationForm, self).save(commit=commit)
        if new:
            site = Site.objects.get_current()
            send_notify_email(
                'New organization in MIL/PEER',
                '''New organization in MIL/PEER: %s. View their profile: https://%s%s.

--
MIL/PEER team.''' % (organization.name, site.domain, organization.get_absolute_url()))
        return organization


class UserCardForm(forms.ModelForm):
    cts = countries

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = UserCard
        exclude = ['_html', 'user']

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs['initial'] = {
                'first_name': kwargs['instance'].user.first_name,
                'last_name': kwargs['instance'].user.last_name,
            }
        super(UserCardForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.user.first_name = self.cleaned_data.get('first_name', '')
        self.instance.user.last_name = self.cleaned_data.get('last_name', '')
        self.instance.user.save()
        return super(UserCardForm, self).save(*args, **kwargs)
