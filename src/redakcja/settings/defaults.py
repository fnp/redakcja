# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'db',
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'NAME': os.environ.get('POSTGRES_USER'),
    }
}

DEBUG = False

ADMINS = (
    (u'Radek Czajka', 'radoslaw.czajka@nowoczesnapolska.org.pl'),
)

INTERNAL_IPS = ['127.0.0.1']

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True


# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/app/var/media'
STATIC_ROOT = '/app/var/static'
CATALOGUE_REPO_PATH = '/app/var/dvcs'
CATALOGUE_IMAGE_REPO_PATH = '/app/var/dvcs-img'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

SESSION_COOKIE_NAME = "redakcja_sessionid"

IMAGE_DIR = 'images/'

CAS_SERVER_URL = None
CAS_APPLY_ATTRIBUTES_TO_USER = True
CAS_RENAME_ATTRIBUTES = {
    'email': 'email', 'firstname': 'first_name', 'lastname': 'last_name'}


LITERARY_DIRECTOR_USERNAME = ''

LEGIMI_USERNAME = None
LEGIMI_PASSWORD = None
LEGIMI_PUBLISHER_ID = None

MIN_COVER_SIZE = (800, 800)

REMOTE_BUILD_URL = os.environ.get('REMOTE_BUILD_URL')
REMOTE_BUILD_TOKEN = os.environ.get('REMOTE_BUILD_TOKEN')
