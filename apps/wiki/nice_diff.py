# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import difflib
import re

from django.template.loader import render_to_string
from django.utils.html import escape as html_escape

DIFF_RE = re.compile(r"""\x00([+^-])""", re.UNICODE)
NAMES = {'+': 'added', '-': 'removed', '^': 'changed'}


def diff_replace(match):
    return """<span class="diff_mark diff_mark_%s">""" % NAMES[match.group(1)]


def filter_line(line):
    return  DIFF_RE.sub(diff_replace, html_escape(line)).replace('\x01', '</span>')


def html_diff_table(la, lb):
    return render_to_string("wiki/diff_table.html", {
        "changes": [(a[0], filter_line(a[1]), b[0], filter_line(b[1]), change)
                        for a, b, change in difflib._mdiff(la, lb)],
    })


__all__ = ['html_diff_table']
