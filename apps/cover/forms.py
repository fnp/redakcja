# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from cover.models import Image
from django.utils.text import mark_safe

from cover.utils import get_flickr_data, FlickrError


class ImageAddForm(forms.ModelForm):
    class Meta:
        model = Image

    def __init__(self, *args, **kwargs):
        super(ImageAddForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False

    def clean_download_url(self):
        cl = self.cleaned_data['download_url'] or None
        if cl is not None:
            try:
                img = Image.objects.get(download_url=cl)
            except Image.DoesNotExist:
                pass
            else:
                raise forms.ValidationError(mark_safe(
                    ugettext('Image <a href="%(url)s">already in repository</a>.')
                    % {'url': img.get_absolute_url()}))
        return cl

    def clean(self):
        cleaned_data = super(ImageAddForm, self).clean()
        if not cleaned_data.get('download_url', None) and not cleaned_data.get('file', None):
            raise forms.ValidationError('No image specified')
        return cleaned_data


class ImageEditForm(forms.ModelForm):
    """Form used for editing a Book."""
    class Meta:
        model = Image
        exclude = ['download_url']


class ReadonlyImageEditForm(ImageEditForm):
    """Form used for not editing an Image."""

    def __init__(self, *args, **kwargs):
        super(ReadonlyImageEditForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"readonly": True})

    def save(self, *args, **kwargs):
        raise AssertionError("ReadonlyImageEditForm should not be saved.")


class FlickrForm(forms.Form):
    source_url = forms.URLField(label=_('Flickr URL'))

    def clean_source_url(self):
        url = self.cleaned_data['source_url']
        try:
            flickr_data = get_flickr_data(url)
        except FlickrError as e:
            raise forms.ValidationError(e)
        for field_name in ('license_url', 'license_name', 'author', 'title', 'download_url'):
            self.cleaned_data[field_name] = flickr_data[field_name]
        return flickr_data['source_url']
