# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue.models import Category
from catalogue.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from catalogue.constants import MASTERS
from catalogue.models import Document


def tag_field(category_tag, required=True):
    category = Category.objects.get(dc_tag=category_tag)
    return forms.ModelMultipleChoiceField(queryset=category.tag_set.all(), required=required)


class DocumentCreateForm(forms.Form):
    """
        Form used for creating new documents.
    """
    owner_organization = forms.CharField(required=False)
    title = forms.CharField()
    language = forms.CharField()
    publisher = forms.CharField(required=False)
    description = forms.CharField(required=False)
    rights = forms.CharField(required=False)
    audience = forms.CharField()
    
    cover = forms.FileField(required=False)
    
    # summary = forms.CharField(required=True)
    # template = forms.ModelChoiceField(Template.objects, required=False)
    #
    # def __init__(self, *args, org=None, **kwargs):
    #     super(DocumentCreateForm, self).__init__(*args, **kwargs)
    #     self.fields['title'].widget.attrs={'class': 'autoslug-source'}
    #     self.fields['template'].queryset = Template.objects.filter(is_main=True)
    #
    # def clean(self):
    #     super(DocumentCreateForm, self).clean()
    #     template = self.cleaned_data['template']
    #
    #     if template is not None:
    #         self.cleaned_data['text'] = template.content
    #
    #     if not self.cleaned_data.get("text"):
    #         self._errors["template"] = self.error_class([_("You must select a template")])
    #
    #     return self.cleaned_data

    def clean_cover(self):
        cover = self.cleaned_data['cover']
        if cover.name.rsplit('.', 1)[-1].lower() not in ('jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'):
            raise forms.ValidationError(_('The cover should be an image file (jpg/png/gif)'))
        return file


class DocumentsUploadForm(forms.Form):
    """
        Form used for uploading new documents.
    """
    file = forms.FileField(required=True, label=_('ZIP file'))
    dirs = forms.BooleanField(
        label=_('Directories are documents in chunks'),
        widget=forms.CheckboxInput(attrs={'disabled': 'disabled'}))

    def clean(self):
        file = self.cleaned_data['file']

        import zipfile
        try:
            z = self.cleaned_data['zip'] = zipfile.ZipFile(file)
        except zipfile.BadZipfile:
            raise forms.ValidationError("Should be a ZIP file.")
        if z.testzip():
            raise forms.ValidationError("ZIP file corrupt.")

        return self.cleaned_data


class ChooseMasterForm(forms.Form):
    """
        Form used for fixing the chunks in a book.
    """

    master = forms.ChoiceField(choices=((m, m) for m in MASTERS))


class DocumentForkForm(forms.Form):
    """
        Form used for forking documents.
    """
    owner_organization = forms.CharField(required=False)
