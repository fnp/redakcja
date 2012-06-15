#
# Nose tests
#

from redakcja.settings.common import *

# ROOT_URLCONF = 'yourapp.settings.test.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

import tempfile

CATALOGUE_REPO_PATH = tempfile.mkdtemp(prefix='redakcja-repo')
MEDIA_ROOT = tempfile.mkdtemp(prefix='media-root')
USE_CELERY = False

INSTALLED_APPS += ('django_nose', 'dvcs.tests')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_MODULES = ('catalogue', 'cover', 'dvcs.tests', 'wiki', 'toolbar')
COVER_APPS = ('catalogue', 'cover', 'dvcs', 'wiki', 'toolbar')
NOSE_ARGS = (
    '--tests=' + ','.join(TEST_MODULES),
    '--cover-package=' + ','.join(COVER_APPS),
    '-d',
    '--with-doctest',
    '--with-xunit',
    '--with-xcoverage',
)
