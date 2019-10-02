#!/usr/bin/env python
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "redakcja.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
