# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.translation import ugettext_lazy as _

TRIM_BEGIN = " TRIM_BEGIN "
TRIM_END = " TRIM_END "

MASTERS = ['powiesc',
           'opowiadanie',
           'liryka_l',
           'liryka_lp',
           'dramat_wierszowany_l',
           'dramat_wierszowany_lp',
           'dramat_wspolczesny',
           ]

STAGES = [
    ('Draft', _('Draft')),
    ('Comments', _('Comments')),
    ('Comments review', _('Comments review')),
    ('Proofreading', _('Proofreading')),
    ('Publication', _('Publication')),
]
