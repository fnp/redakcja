# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from wiki.models import Book, Chunk
from django.utils.translation import ugettext_lazy as _

from dvcs.models import Tag
from wiki.constants import MASTERS

class DocumentTagForm(forms.Form):
    """
        Form for tagging revisions.
    """

    id = forms.CharField(widget=forms.HiddenInput)
    tag = forms.ModelChoiceField(queryset=Tag.objects.all())
    revision = forms.IntegerField(widget=forms.HiddenInput)


class DocumentCreateForm(forms.ModelForm):
    """
        Form used for creating new documents.
    """
    file = forms.FileField(required=False)
    text = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Book
        exclude = ['gallery']

    def clean(self):
        super(DocumentCreateForm, self).clean()
        file = self.cleaned_data['file']

        if file is not None:
            try:
                self.cleaned_data['text'] = file.read().decode('utf-8')
            except UnicodeDecodeError:
                raise forms.ValidationError("Text file must be UTF-8 encoded.")

        if not self.cleaned_data["text"]:
            raise forms.ValidationError("You must either enter text or upload a file")

        return self.cleaned_data


class DocumentsUploadForm(forms.Form):
    """
        Form used for uploading new documents.
    """
    file = forms.FileField(required=True, label=_('ZIP file'))

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


class DocumentTextSaveForm(forms.Form):
    """
    Form for saving document's text:

        * parent_revision - revision which the modified text originated from.
        * comment - user's verbose comment; will be used in commit.
        * stage_completed - mark this change as end of given stage.

    """

    parent_revision = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.HiddenInput)

    author_name = forms.CharField(
        required=False,
        label=_(u"Author"),
        help_text=_(u"Your name"),
    )

    author_email = forms.EmailField(
        required=False,
        label=_(u"Author's email"),
        help_text=_(u"Your email address, so we can show a gravatar :)"),
    )

    comment = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label=_(u"Your comments"),
        help_text=_(u"Describe changes you made."),
    )

    stage_completed = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_(u"Completed"),
        help_text=_(u"If you completed a life cycle stage, select it."),
    )


class DocumentTextRevertForm(forms.Form):
    """
    Form for reverting document's text:

        * revision - revision to revert to.
        * comment - user's verbose comment; will be used in commit.

    """

    revision = forms.IntegerField(widget=forms.HiddenInput)

    author_name = forms.CharField(
        required=False,
        label=_(u"Author"),
        help_text=_(u"Your name"),
    )

    author_email = forms.EmailField(
        required=False,
        label=_(u"Author's email"),
        help_text=_(u"Your email address, so we can show a gravatar :)"),
    )

    comment = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label=_(u"Your comments"),
        help_text=_(u"Describe the reason for reverting."),
    )


class ChunkForm(forms.ModelForm):
    """
        Form used for editing a chunk.
    """

    class Meta:
        model = Chunk
        exclude = ['number']

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        try:
            chunk = Chunk.objects.get(book=self.instance.book, slug=slug)
        except Chunk.DoesNotExist:
            return slug
        if chunk == self:
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

    append_to = forms.ModelChoiceField(queryset=Book.objects.all())


class BookForm(forms.ModelForm):
    """
        Form used for editing a Book.
    """

    class Meta:
        model = Book


class ChooseMasterForm(forms.Form):
    """
        Form used for fixing the chunks in a book.
    """

    master = forms.ChoiceField(choices=((m, m) for m in MASTERS))
