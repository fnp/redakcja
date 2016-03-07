# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue.models import User
from django.db.models import Count
from django import forms
from django.utils.translation import ugettext_lazy as _

from catalogue.constants import MASTERS
from catalogue.models import Document, Template

class DocumentCreateForm(forms.Form):
    """
        Form used for creating new documents.
    """
    owner_organization = forms.CharField(required=False)
    title = forms.CharField(required=True)
    language = forms.CharField(required=True)
    publisher = forms.CharField(required=False)
    description = forms.CharField(required=False)
    rights = forms.CharField(required=False)
    audience = forms.CharField()
    
    cover = forms.FileField(required=False)
    
    #summary = forms.CharField(required=True)
    #template = forms.ModelChoiceField(Template.objects, required=False)

    #class Meta:
        #model = Book
        #exclude = ['parent', 'parent_number', 'project', 'gallery', 'public']

    #def __init__(self, *args, org=None, **kwargs):
    #    super(DocumentCreateForm, self).__init__(*args, **kwargs)
        #self.fields['slug'].widget.attrs={'class': 'autoslug'}
        #self.fields['title'].widget.attrs={'class': 'autoslug-source'}
        #self.fields['template'].queryset = Template.objects.filter(is_main=True)

    #~ def clean(self):
        #~ super(DocumentCreateForm, self).clean()
        #template = self.cleaned_data['template']
        #self.cleaned_data['gallery'] = self.cleaned_data['slug']

        #~ if template is not None:
            #~ self.cleaned_data['text'] = template.content

        #~ if not self.cleaned_data.get("text"):
            #~ self._errors["template"] = self.error_class([_("You must select a template")])

        #~ return self.cleaned_data


class DocumentsUploadForm(forms.Form):
    """
        Form used for uploading new documents.
    """
    file = forms.FileField(required=True, label=_('ZIP file'))
    dirs = forms.BooleanField(label=_('Directories are documents in chunks'),
            widget = forms.CheckboxInput(attrs={'disabled':'disabled'}))

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


class DocumentForm(forms.ModelForm):
    """
        Form used for editing a chunk.
    """
    user = forms.ModelChoiceField(queryset=
        User.objects.order_by('last_name', 'first_name'), required=False,
        label=_('Assigned to')) 

    class Meta:
        model = Document
        fields = ['user', 'stage']


class DocumentAddForm(DocumentForm):
    """
        Form used for adding a chunk to a document.
    """

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        try:
            user = Chunk.objects.get(book=self.instance.book, slug=slug)
        except Chunk.DoesNotExist:
            return slug
        raise forms.ValidationError(_('Chunk with this slug already exists'))


class BookForm(forms.ModelForm):
    """Form used for editing a Book."""

    class Meta:
        model = Document
        exclude = ['project']

    def __init__(self, *args, **kwargs):
        ret = super(BookForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs.update({"class": "autoslug"})
        self.fields['title'].widget.attrs.update({"class": "autoslug-source"})
        return ret


class ReadonlyBookForm(BookForm):
    """Form used for not editing a Book."""

    def __init__(self, *args, **kwargs):
        ret = super(ReadonlyBookForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"readonly": True})
        return ret


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
