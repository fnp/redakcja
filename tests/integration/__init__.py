# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
from django.conf import settings

if not os.path.exists(settings.STATIC_ROOT_SYMLINK):
    os.symlink(settings.STATIC_ROOT, settings.STATIC_ROOT_SYMLINK)
