# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from modeltranslation.translator import translator, TranslationOptions
from catalogue.models import Tag, Category


class TagTranslationOptions(TranslationOptions):
    fields = ('label', 'help_text')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('label', 'tutorial')


translator.register(Tag, TagTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
