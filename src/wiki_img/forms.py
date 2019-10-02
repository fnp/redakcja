# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _
from wiki.forms import DocumentTextSaveForm
from catalogue.models import Image


class ImageSaveForm(DocumentTextSaveForm):
    """Form for saving document's text."""

    stage_completed = forms.ModelChoiceField(
        queryset=Image.tag_model.objects.all(),
        required=False,
        label=_(u"Completed"),
        help_text=_(u"If you completed a life cycle stage, select it."),
    )
