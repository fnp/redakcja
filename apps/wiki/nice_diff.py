# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import difflib
import re
from collections import deque

from django.template.loader import render_to_string
from django.utils.html import escape as html_escape

DIFF_RE = re.compile(r"""\x00([+^-])""", re.UNICODE)
NAMES = {'+': 'added', '-': 'removed', '^': 'changed'}


def diff_replace(match):
    return """<span class="diff_mark diff_mark_%s">""" % NAMES[match.group(1)]


def filter_line(line):
    return DIFF_RE.sub(diff_replace, html_escape(line)).replace('\x01', '</span>')


def format_changeset(a, b, change):
    return a[0], filter_line(a[1]), b[0], filter_line(b[1]), change


def html_diff_table(la, lb, context=None):
    all_changes = difflib._mdiff(la, lb)

    if context is None:
        changes = (format_changeset(*c) for c in all_changes)
    else:
        changes = []
        q = deque()
        after_change = False

        for changeset in all_changes:
            q.append(changeset)

            if changeset[2]:
                after_change = True
                if not after_change:
                    changes.append((0, '-----', 0, '-----', False))
                changes.extend(format_changeset(*c) for c in q)
                q.clear()
            else:
                if len(q) == context and after_change:
                    changes.extend(format_changeset(*c) for c in q)
                    q.clear()
                    after_change = False
                elif len(q) > context:
                    q.popleft()

    return render_to_string("wiki/diff_table.html", {
        "changes": changes,
    })


__all__ = ['html_diff_table']
