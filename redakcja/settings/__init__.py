# -*- coding: utf-8 -*-
from __future__ import absolute_import
from os import path
from redakcja.settings.common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(PROJECT_ROOT, 'dev.sqlite'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

LOGGING_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', ('logging.cfg' if not DEBUG else 'logging.cfg.dev'))
try:
    import logging

    if os.path.isfile(LOGGING_CONFIG_FILE):
        import logging.config
        logging.config.fileConfig(LOGGING_CONFIG_FILE)
    else:
        import sys
        logging.basicConfig(stream=sys.stderr)
except (ImportError,), exc:
    raise


try:
    from redakcja.localsettings import *
except ImportError:
    pass
