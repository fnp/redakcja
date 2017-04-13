# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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
    publisher = forms.CharField(required=False)
    description = forms.CharField(required=False)
    cover = forms.FileField(required=False)

    def clean_cover(self):
        cover = self.cleaned_data['cover']
        if cover and cover.name.rsplit('.', 1)[-1].lower() not in ('jpg', 'jpeg', 'png', 'gif', 'svg'):
            raise forms.ValidationError(_('The cover should be an image file (jpg/png/gif)'))
        return file


class TagForm(forms.Form):
    def __init__(self, category, instance=None, tutorial_no=None, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.category = category
        self.instance = instance
        self.field().queryset = Tag.objects.filter(category=self.category)
        self.field().label = self.category.label.capitalize()
        if tutorial_no and category.tutorial:
            self.field().widget.attrs.update({
                'data-toggle': 'tutorial',
                'data-tutorial': str(tutorial_no),
                'data-placement': 'bottom',
                'data-content': category.tutorial,
            })
        if self.instance:
            self.field().initial = self.initial()

    def save(self, instance=None):
        instance = instance or self.instance
        assert instance, 'No instance provided'
        instance.tags.remove(*instance.tags.filter(category=self.category))
        instance.tags.add(*self.cleaned_tags())

    def field(self):
        raise NotImplementedError

    def initial(self):
        raise NotImplementedError

    def cleaned_tags(self):
        raise NotImplementedError

    def metadata_rows(self):
        return '\n'.join(
            '<dc:%(name)s>%(value)s</dc:%(name)s>' % {'name': tag.category.dc_tag, 'value': tag.dc_value}
            for tag in self.cleaned_tags())


class TagSelect(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        help_html = ''
        if option_value:
            tag = Tag.objects.get(id=int(option_value))
            if tag.help_text:
                help_html = mark_safe(' data-help="%s"' % tag.help_text)
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html(
            u'<option value="{}"{}{}>{}</option>',
            option_value, selected_html, help_html, force_text(option_label))


class TagSingleForm(TagForm):
    tag = forms.ModelChoiceField(
        Tag.objects.none(),
        widget=TagSelect(attrs={
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
