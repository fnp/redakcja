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
import tempfile

CATALOGUE_REPO_PATH = tempfile.mkdtemp(prefix='redakcja-repo')
CATALOGUE_IMAGE_REPO_PATH = tempfile.mkdtemp(prefix='redakcja-repo-img')
MEDIA_ROOT = tempfile.mkdtemp(prefix='media-root')
CELERY_ALWAYS_EAGER = True

INSTALLED_APPS += ('dvcs.tests',)

SECRET_KEY = "not-so-secret"


LITERARY_DIRECTOR_USERNAME = 'Kaowiec'
