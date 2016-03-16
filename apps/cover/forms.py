# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import re
from urllib2 import urlopen
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from cover.models import Image
from django.utils.text import mark_safe

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
                    ugettext('Image <a href="%(url)s">already in repository</a>.'
                        ) % {'url': img.get_absolute_url()}))
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
        ret = super(ReadonlyImageEditForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"readonly": True})
        return ret

    def save(self, *args, **kwargs):
        raise AssertionError, "ReadonlyImageEditForm should not be saved."


class FlickrForm(forms.Form):
    source_url = forms.URLField(label=_('Flickr URL'))

    def clean_source_url(self):
        def normalize_html(html):
            return html
            return re.sub('[\t\n]', '', html)
    
        url = self.cleaned_data['source_url']
        m = re.match(r'(https?://)?(www\.|secure\.)?flickr\.com/photos/(?P<author>[^/]+)/(?P<img>\d+)/?', url)
        if not m:
            raise forms.ValidationError("It doesn't look like Flickr URL.")
        author_slug, img_id = m.group('author'), m.group('img')
        base_url = "https://www.flickr.com/photos/%s/%s/" % (author_slug, img_id)

        try:
            html = normalize_html(urlopen(url).read().decode('utf-8'))
        except:
            raise forms.ValidationError('Error reading page.')
        match = re.search(r'<a href="([^"]*)"[^>]* rel="license ', html)
        try:
            assert match
            license_url = match.group(1)
            self.cleaned_data['license_url'] = license_url
            re_license = re.compile(r'https?://creativecommons.org/licenses/([^/]*)/([^/]*)/.*')
            m = re_license.match(license_url)
            assert m
            self.cleaned_data['license_name'] = 'CC %s %s' % (m.group(1).upper(), m.group(2))
        except AssertionError:
            raise forms.ValidationError('Error reading license name.')

        m = re.search(r'<a[^>]* class="owner-name [^>]*>([^<]*)<', html)
        if m:
            self.cleaned_data['author'] = "%s@Flickr" % m.group(1)
        else:
            raise forms.ValidationError('Error reading author name.')

        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
        if not m:
            raise forms.ValidationError('Error reading image title.')
        self.cleaned_data['title'] = m.group(1).strip()

        m = re.search(r'modelExport: (\{.*\})', html)
        try:
            assert m
            self.cleaned_data['download_url'] = 'https:' + json.loads(m.group(1))['photo-models'][0]['sizes']['o']['url']
        except (AssertionError, ValueError, IndexError, KeyError):
            raise forms.ValidationError('Error reading image URL.')
        return base_url
