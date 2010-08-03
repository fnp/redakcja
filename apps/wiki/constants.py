# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

DOCUMENT_STAGES = (
    ("", u"-----"),
    ("first_correction", _(u"First correction")),
    ("tagging", _(u"Tagging")),
    ("proofreading", _(u"Initial Proofreading")),
    ("annotation-proofreading", _(u"Annotation Proofreading")),
    ("modernisation", _(u"Modernisation")),
    ("themes", _(u"Themes")),
    ("editor-proofreading", _(u"Editor's Proofreading")),
    ("technical-editor-proofreading", _(u"Technical Editor's Proofreading")),
)

DOCUMENT_TAGS = DOCUMENT_STAGES + \
    (("ready-to-publish", _(u"Ready to publish")),)

DOCUMENT_TAGS_DICT = dict(DOCUMENT_TAGS)
DOCUMENT_STAGES_DICT = dict(DOCUMENT_STAGES)
