# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import tempfile
from redakcja.settings import *


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

CATALOGUE_REPO_PATH = tempfile.mkdtemp(prefix='redakcja-repo')
CATALOGUE_IMAGE_REPO_PATH = tempfile.mkdtemp(prefix='redakcja-repo-img')
MEDIA_ROOT = tempfile.mkdtemp(prefix='media-root')

INSTALLED_APPS += ('dvcs.tests',)

SECRET_KEY = "not-so-secret"


LITERARY_DIRECTOR_USERNAME = 'Kaowiec'
