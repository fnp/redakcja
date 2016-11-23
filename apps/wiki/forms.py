# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _

from catalogue.models import Chunk


class DocumentPubmarkForm(forms.Form):
    """
        Form for marking revisions for publishing.
    """

    id = forms.CharField(widget=forms.HiddenInput)
    publishable = forms.BooleanField(required=False, initial=True, label=_('Publishable'))
    revision = forms.IntegerField(widget=forms.HiddenInput)


class DocumentTextSaveForm(forms.Form):
    """
    Form for saving document's text:

        * parent_revision - revision which the modified text originated from.
        * comment - user's verbose comment; will be used in commit.
        * stage_completed - mark this change as end of given stage.

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

    stage_completed = forms.ModelChoiceField(
        queryset=Chunk.tag_model.objects.all(),
        required=False,
        label=_(u"Completed"),
        help_text=_(u"If you completed a life cycle stage, select it."),
    )

    publishable = forms.BooleanField(
        required=False, initial=False,
        label=_('Publishable'),
        help_text=_(u"Mark this revision as publishable."))

    for_cybernauts = forms.BooleanField(
        required=False, initial=False,
        label=_(u"For Cybernauts"),
        help_text=_(u"Mark this document for Cybernauts.")
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.chunk = kwargs.pop('chunk')
        super(DocumentTextSaveForm, self).__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated():
            self.fields['author_name'].required = False
            self.fields['author_email'].required = False
        self.fields['for_cybernauts'].initial = self.chunk.book.for_cybernauts

    def save(self):
        if self.user.is_authenticated():
            author = self.user
        else:
            author = None
        text = self.cleaned_data['text']
        parent_revision = self.cleaned_data['parent_revision']
        if parent_revision is not None:
            parent = self.chunk.at_revision(parent_revision)
        else:
            parent = None
        stage = self.cleaned_data['stage_completed']
        tags = [stage] if stage else []
        publishable = self.cleaned_data['publishable'] and self.user.has_perm('catalogue.can_pubmark')
        self.chunk.commit(
            author=author,
            text=text,
            parent=parent,
            description=self.cleaned_data['comment'],
            tags=tags,
            author_name=self.cleaned_data['author_name'],
            author_email=self.cleaned_data['author_email'],
            publishable=publishable)
        self.chunk.book.for_cybernauts = self.cleaned_data['for_cybernauts']
        self.chunk.book.save()


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
