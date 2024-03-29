# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django import forms
import json

from toolbar import models


class ButtonAdminForm(forms.ModelForm):
    class Meta:
        model = models.Button
        exclude = []

    def clean_params(self):
        value = self.cleaned_data['params']
        try:
            return json.dumps(json.loads(value))
        except ValueError as e:
            raise forms.ValidationError(e)


class ButtonAdmin(admin.ModelAdmin):
    form = ButtonAdminForm
    list_display = ('slug', 'label', 'tooltip', 'accesskey', 'scriptlet')
    list_display_links = ('slug',)
    list_editable = ('label', 'tooltip', 'accesskey')
    prepopulated_fields = {'slug': ('label',)}

admin.site.register(models.Button, ButtonAdmin)
admin.site.register(models.ButtonGroup)
admin.site.register(models.Scriptlet)
