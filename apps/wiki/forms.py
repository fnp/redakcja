# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from wiki.constants import DOCUMENT_TAGS, DOCUMENT_STAGES
from django.utils.translation import ugettext_lazy as _


class DocumentTagForm(forms.Form):
    """
        Form for tagging revisions.
    """

    id = forms.CharField(widget=forms.HiddenInput)
    tag = forms.ChoiceField(choices=DOCUMENT_TAGS)
    revision = forms.IntegerField(widget=forms.HiddenInput)


class DocumentCreateForm(forms.Form):
    """
        Form used for creating new documents.
    """
    title = forms.CharField()
    id = forms.RegexField(regex=ur"\w+")
    file = forms.FileField(required=False)
    text = forms.CharField(required=False, widget=forms.Textarea)

    def clean(self):
        file = self.cleaned_data['file']

        if file is not None:
            try:
                self.cleaned_data['text'] = file.read().decode('utf-8')
            except UnicodeDecodeError:
                raise forms.ValidationError("Text file must be UTF-8 encoded.")

        if not self.cleaned_data["text"]:
            raise forms.ValidationError("You must either enter text or upload a file")

        return self.cleaned_data


class DocumentTextSaveForm(forms.Form):
    """
    Form for saving document's text:

        * name - document's storage identifier.
        * parent_revision - revision which the modified text originated from.
        * comment - user's verbose comment; will be used in commit.
        * stage_completed - mark this change as end of given stage.

    """

    id = forms.CharField(widget=forms.HiddenInput)
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

    stage_completed = forms.ChoiceField(
        choices=DOCUMENT_STAGES,
        required=False,
        label=_(u"Completed"),
        help_text=_(u"If you completed a life cycle stage, select it."),
    )
