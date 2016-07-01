# -*- coding: utf-8 -*-
import os
from django.conf import settings

if not os.path.exists(settings.STATIC_ROOT_SYMLINK):
    os.symlink(settings.STATIC_ROOT, settings.STATIC_ROOT_SYMLINK)
