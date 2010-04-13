# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

DOCUMENT_TAGS = (
    ("source", _("Tekst źródłowy")),
    ("first_correction", _("Po autokorekcie")),
    ("tagged", _("Tekst otagowany")),
    ("second_correction", _("Po korekcie")),
    ("source_annotations", _("Sprawdzone przypisy źródła")),
    ("language_updates", _("Uwspółcześnienia")),
    ("ready_to_publish", _("Tekst do publikacji")),
)

DOCUMENT_TAGS_DICT = dict(DOCUMENT_TAGS)

DOCUMENT_STAGES = (
    ("first_correction", _("Autokorekta")),
    ("tagged", _("Tagowanie")),
    ("second_correction", _("Korekta")),
    ("source_annotations", _("Przypisy źródła")),
    ("language_updates", _("Uwspółcześnienia")),
)

DOCUMENT_STAGES_DICT = dict(DOCUMENT_STAGES)
