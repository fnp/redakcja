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
from catalogue.models import Book, Chunk, Template

class DocumentCreateForm(forms.ModelForm):
    """
        Form used for creating new documents.
    """
    file = forms.FileField(required=False)
    template = forms.ModelChoiceField(Template.objects, required=False)
    text = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Book
        exclude = ['parent', 'parent_number', 'project']

    def __init__(self, *args, **kwargs):
        super(DocumentCreateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs={'class': 'autoslug'}
        self.fields['gallery'].widget.attrs={'class': 'autoslug'}
        self.fields['title'].widget.attrs={'class': 'autoslug-source'}
        self.fields['template'].queryset = Template.objects.filter(is_main=True)

    def clean(self):
        super(DocumentCreateForm, self).clean()
        file = self.cleaned_data['file']
        template = self.cleaned_data['template']

        if file is not None:
            try:
                self.cleaned_data['text'] = file.read().decode('utf-8')
            except UnicodeDecodeError:
                raise forms.ValidationError(_("Text file must be UTF-8 encoded."))
        elif template is not None:
            self.cleaned_data['text'] = template.content

        if not self.cleaned_data["text"]:
            self._errors["file"] = self.error_class([_("You must enter text, upload a file or select a template")])

        return self.cleaned_data


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


class ChunkForm(forms.ModelForm):
    """
        Form used for editing a chunk.
    """
    user = forms.ModelChoiceField(queryset=
        User.objects.annotate(count=Count('chunk')).
        order_by('last_name', 'first_name'), required=False,
        label=_('Assigned to')) 

    class Meta:
        model = Chunk
        fields = ['title', 'slug', 'gallery_start', 'user', 'stage']
        exclude = ['number']

    def __init__(self, *args, **kwargs):
        super(ChunkForm, self).__init__(*args, **kwargs)
        self.fields['gallery_start'].widget.attrs={'class': 'number-input'}
        self.fields['slug'].widget.attrs={'class': 'autoslug'}
        self.fields['title'].widget.attrs={'class': 'autoslug-source'}

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        try:
            chunk = Chunk.objects.get(book=self.instance.book, slug=slug)
        except Chunk.DoesNotExist:
            return slug
        if chunk == self.instance:
            return slug
        raise forms.ValidationError(_('Chunk with this slug already exists'))


class ChunkAddForm(ChunkForm):
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


class BookAppendForm(forms.Form):
    """
        Form for appending a book to another book.
        It means moving all chunks from book A to book B and deleting A.
    """
    append_to = forms.ModelChoiceField(queryset=Book.objects.all(),
            label=_("Append to"))

    def __init__(self, book, *args, **kwargs):
        ret =  super(BookAppendForm, self).__init__(*args, **kwargs)
        self.fields['append_to'].queryset = Book.objects.exclude(pk=book.pk)
        return ret


class BookForm(forms.ModelForm):
    """Form used for editing a Book."""

    class Meta:
        model = Book
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
