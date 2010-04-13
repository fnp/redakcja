# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

DOCUMENT_TAGS = (
    ("source", _(u"Tekst źródłowy")),
    ("first_correction", _(u"Po autokorekcie")),
    ("tagged", _(u"Tekst otagowany")),
    ("second_correction", _(u"Po korekcie")),
    ("source_annotations", _(u"Sprawdzone przypisy źródła")),
    ("language_updates", _(u"Uwspółcześnienia")),
    ("ready_to_publish", _(u"Tekst do publikacji")),
)

DOCUMENT_TAGS_DICT = dict(DOCUMENT_TAGS)

DOCUMENT_STAGES = (
    ("first_correction", _(u"Autokorekta")),
    ("tagged", _(u"Tagowanie")),
    ("second_correction", _(u"Korekta")),
    ("source_annotations", _(u"Przypisy źródła")),
    ("language_updates", _(u"Uwspółcześnienia")),
)

DOCUMENT_STAGES_DICT = dict(DOCUMENT_STAGES)
