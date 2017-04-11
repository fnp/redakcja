# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue.models import Category
from catalogue.models import Tag
from django import forms
from django.utils.translation import ugettext_lazy as _

from catalogue.constants import MASTERS


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

    def clean_cover(self):
        cover = self.cleaned_data['cover']
        if cover and cover.name.rsplit('.', 1)[-1].lower() not in ('jpg', 'jpeg', 'png', 'gif', 'svg'):
            raise forms.ValidationError(_('The cover should be an image file (jpg/png/gif)'))
        return file


class TagForm(forms.Form):
    def __init__(self, category, instance=None, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.category = category
        self.instance = instance
        self.field().queryset = Tag.objects.filter(category=self.category)
        self.field().label = self.category.label.capitalize()
        if self.instance:
            self.field().initial = self.initial()

    def save(self):
        assert self.instance, 'No instance provided'
        self.instance.tags.remove(*self.instance.tags.filter(category=self.category))
        self.instance.tags.add(self.cleaned_tags())

    def field(self):
        raise NotImplementedError

    def initial(self):
        raise NotImplementedError

    def cleaned_tags(self):
        raise NotImplementedError


class TagSingleForm(TagForm):
    tag = forms.ModelChoiceField(
        Tag.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    def field(self):
        return self.fields['tag']

    def initial(self):
        return self.instance.tags.get(category=self.category)

    def cleaned_tags(self):
        return [self.cleaned_data['tag']]


class TagMultipleForm(TagForm):
    tags = forms.ModelMultipleChoiceField(
        Tag.objects.none(), required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'chosen-select',
            'data-placeholder': _('Choose'),
        }))

    def field(self):
        return self.fields['tags']

    def initial(self):
        return self.instance.tags.filter(category=self.category)

    def cleaned_tags(self):
        return self.cleaned_data['tags']


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
