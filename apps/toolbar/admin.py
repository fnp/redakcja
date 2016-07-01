# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
import json

from toolbar import models


class ButtonAdminForm(forms.ModelForm):
    class Meta:
        model = models.Button

    def clean_params(self):
        value = self.cleaned_data['params']
        try:
            return json.dumps(json.loads(value))
        except ValueError, e:
            raise forms.ValidationError(e)


class ButtonAdmin(admin.ModelAdmin):
    form = ButtonAdminForm
    list_display = ('slug', 'label', 'tooltip', 'accesskey')
    list_display_links = ('slug',)
    list_editable = ('label', 'tooltip', 'accesskey')
    prepopulated_fields = {'slug': ('label',)}

admin.site.register(models.Button, ButtonAdmin)
admin.site.register(models.ButtonGroup)
admin.site.register(models.Scriptlet)
