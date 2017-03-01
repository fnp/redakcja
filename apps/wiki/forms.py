# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from catalogue.constants import STAGES
from librarian.document import Document


class DocumentTextSaveForm(forms.Form):
    """
    Form for saving document's text:

        * parent_revision - revision which the modified text originated from.
        * comment - user's verbose comment; will be used in commit.
        * stage - change to this stage

    """

    parent_revision = forms.IntegerField(widget=forms.HiddenInput, required=False)
    text = forms.CharField(widget=forms.HiddenInput)

    author_name = forms.CharField(
        required=True,
        label=_(u"Author"),
        help_text=_(u"Your name"),
    )

    author_email = forms.EmailField(
        required=True,
        label=_(u"Author's email"),
        help_text=_(u"Your email address, so we can show a gravatar :)"),
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label=_(u"Your comments"),
        help_text=_(u"Describe changes you made."),
    )

    stage = forms.ChoiceField(
        choices=[(s, s) for s in STAGES],
        required=False,
        label=_(u"Stage"),
        help_text=_(u"If completed a work stage, change to another one."),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DocumentTextSaveForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated():
            self.fields['author_name'].required = False
            self.fields['author_email'].required = False

    def clean_text(self):
        text = self.cleaned_data['text']
        try:
            doc = Document.from_string(text)
        except ValueError as e:
            raise ValidationError(e.message)

        from librarian import SSTNS, DCNS
        root_elem = doc.edoc.getroot()
        if len(root_elem) < 1 or root_elem[0].tag != SSTNS('metadata'):
            raise ValidationError("The first tag in section should be metadata")
        if len(root_elem) < 2 or root_elem[1].tag != SSTNS('header'):
            raise ValidationError("The first tag after metadata should be header")
        header = root_elem[1]
        if not getattr(header, 'text', None) or not header.text.strip():
            raise ValidationError(
                "The first header should contain the title in plain text (no links, emphasis etc.) and cannot be empty")

        cover_url = doc.meta.get_one(DCNS('relation.coverimage.url'))
        if cover_url:
            ext = cover_url.rsplit('.', 1)[-1].lower()
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'svg'):
                raise ValidationError('Invalid cover image format, should be an image file (jpg, png, gif, svg). '
                                      'Change it in Metadata.')
        return text


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
        required=False,
        widget=forms.Textarea,
        label=_(u"Your comments"),
        help_text=_(u"Describe the reason for reverting."),
    )


class DocumentTextPublishForm(forms.Form):
    revision = forms.IntegerField(widget=forms.HiddenInput)
