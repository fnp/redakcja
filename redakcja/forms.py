# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        max_length = User._meta.get_field('username').max_length
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            msg = _(
                'User with this email address already exists. '
                '<a href="%(login_url)s">Log in</a> or <a href="%(reset_url)s">reset your password</a>.') % {
                'login_url': reverse('login'),
                'reset_url': reverse('password_reset'),
            }
            raise forms.ValidationError(mark_safe(msg))
        if len(email) > max_length:
            raise forms.ValidationError(_('Username too long. Max length: %s') % max_length)
        return email
