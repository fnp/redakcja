# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import gettext_lazy as _

from documents.models import Chunk


class DocumentPubmarkForm(forms.Form):
    """
        Form for approving revisions.
    """

    id = forms.CharField(widget=forms.HiddenInput)
    publishable = forms.BooleanField(required=False, initial=True,
            label=_('Approved'))
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
        required=True,
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

    publishable = forms.BooleanField(required=False, initial=False,
        label=_('Approve'),
        help_text=_("Approve this revision.")
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        r = super(DocumentTextSaveForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['author_name'].required = False
            self.fields['author_email'].required = False
            try:
                user.profile
            except:
                pass
            else:
                if user.profile.approve_by_default:
                    self.fields['publishable'].initial = True

        return r


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
