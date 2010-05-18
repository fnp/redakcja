#
# Nose tests
#

from redakcja.settings.common import *

# ROOT_URLCONF = 'yourapp.settings.test.urls'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'

import tempfile

WIKI_REPOSITORY_PATH = tempfile.mkdtemp(prefix='wikirepo')

INSTALLED_APPS += ('django_nose',)

TEST_RUNNER = 'django_nose.run_tests'
TEST_MODULES = ('wiki', 'toolbar', 'vstorage')
NOSE_ARGS = (
    '--tests=' + ','.join(TEST_MODULES),
    '--cover-package=' + ','.join(TEST_MODULES),
    '-d',
    '--with-coverage',
    '--with-doctest',
    '--with-xunit',
    '--with-xcoverage',
)
