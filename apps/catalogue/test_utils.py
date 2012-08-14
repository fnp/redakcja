# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""Testing utilities."""

from os.path import abspath, dirname, join


def get_fixture(path):
    f_path = join(dirname(abspath(__file__)), 'tests/files', path)
    with open(f_path) as f:
        return unicode(f.read(), 'utf-8')
