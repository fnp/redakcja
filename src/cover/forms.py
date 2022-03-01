# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from io import BytesIO

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from cover.models import Image
from django.utils.safestring import mark_safe
from PIL import Image as PILImage

from cover.utils import get_import_data, FlickrError, URLOpener


class ImageAddForm(forms.ModelForm):
    class Meta:
        model = Image
        exclude = [] 

    def __init__(self, *args, **kwargs):
        super(ImageAddForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False
        self.fields['use_file'].required = False
        self.fields['cut_top'].required = False
        self.fields['cut_left'].required = False
        self.fields['cut_bottom'].required = False
        self.fields['cut_right'].required = False

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

    def clean_source_url(self):
        source_url = self.cleaned_data['source_url'] or None
        if source_url is not None:
            same_source = Image.objects.filter(source_url=source_url)
            if same_source:
                raise forms.ValidationError(mark_safe(
                    ugettext('Image <a href="%(url)s">already in repository</a>.')
                    % {'url': same_source.first().get_absolute_url()}))
        return source_url

    clean_cut_top = lambda self: self.cleaned_data.get('cut_top') or 0
    clean_cut_bottom = lambda self: self.cleaned_data.get('cut_bottom') or 0
    clean_cut_left = lambda self: self.cleaned_data.get('cut_left') or 0
    clean_cut_right = lambda self: self.cleaned_data.get('cut_right') or 0
    
    def clean(self):
        cleaned_data = super(ImageAddForm, self).clean()
        download_url = cleaned_data.get('download_url', None)
        uploaded_file = cleaned_data.get('file', None)
        if not download_url and not uploaded_file:
            raise forms.ValidationError(ugettext('No image specified'))
        if download_url:
            image_data = URLOpener().open(download_url).read()
            width, height = PILImage.open(BytesIO(image_data)).size
        else:
            width, height = PILImage.open(uploaded_file.file).size
        min_width, min_height = settings.MIN_COVER_SIZE
        if width < min_width or height < min_height:
            raise forms.ValidationError(ugettext('Image too small: %sx%s, minimal dimensions %sx%s') %
                                        (width, height, min_width, min_height))
        return cleaned_data


class ImageEditForm(forms.ModelForm):
    """Form used for editing a Book."""
    class Meta:
        model = Image
        exclude = ['download_url']

    def clean(self):
        cleaned_data = super(ImageEditForm, self).clean()
        uploaded_file = cleaned_data.get('file', None)
        width, height = PILImage.open(uploaded_file.file).size
        min_width, min_height = settings.MIN_COVER_SIZE
        if width < min_width or height < min_height:
            raise forms.ValidationError(ugettext('Image too small: %sx%s, minimal dimensions %sx%s') %
                                        (width, height, min_width, min_height))


class ReadonlyImageEditForm(ImageEditForm):
    """Form used for not editing an Image."""

    def __init__(self, *args, **kwargs):
        super(ReadonlyImageEditForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"readonly": True})

    def save(self, *args, **kwargs):
        raise AssertionError("ReadonlyImageEditForm should not be saved.")


class ImportForm(forms.Form):
    source_url = forms.URLField(label=_('WikiCommons, MNW or Flickr URL'))

    def clean_source_url(self):
        url = self.cleaned_data['source_url']
        try:
            import_data = get_import_data(url)
        except FlickrError as e:
            raise forms.ValidationError(e)
        for field_name in ('license_url', 'license_name', 'author', 'title', 'download_url'):
            self.cleaned_data[field_name] = import_data[field_name]
        return import_data['source_url']

