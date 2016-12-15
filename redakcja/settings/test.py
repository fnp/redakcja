# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
#
# Nose tests
#

from redakcja.settings.common import *
import tempfile

# ROOT_URLCONF = 'yourapp.settings.test.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


CATALOGUE_REPO_PATH = tempfile.mkdtemp(prefix='redakcja-repo')
MEDIA_ROOT = tempfile.mkdtemp(prefix='media-root')
USE_CELERY = False

INSTALLED_APPS += ('django_nose', 'dvcs.tests')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_MODULES = ('catalogue', 'dvcs.tests', 'wiki', 'toolbar')
COVER_APPS = ('catalogue', 'dvcs', 'wiki', 'toolbar')
NOSE_ARGS = (
    '--tests=' + ','.join(TEST_MODULES),
    '--cover-package=' + ','.join(COVER_APPS),
    '-d',
    '--with-doctest',
    '--with-xunit',
    '--with-xcoverage',
)

SECRET_KEY = "not-so-secret"
