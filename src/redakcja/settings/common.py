# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path

PROJECT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

DEBUG = False

MAINTENANCE_MODE = False

ADMINS = (
    (u'Radek Czajka', 'radoslaw.czajka@nowoczesnapolska.org.pl'),
)

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

#import locale
#locale.setlocale(locale.LC_ALL, '')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True


# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/dynamic'
STATIC_ROOT = PROJECT_ROOT + '/../static/'

STATICFILES_DIRS = [
    PROJECT_ROOT + '/static/'
]

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/dynamic/'
STATIC_URL = '/media/static/'

SESSION_COOKIE_NAME = "redakcja_sessionid"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            PROJECT_ROOT + '/templates',
        ],
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "redakcja.context_processors.settings", # this is instead of media
                'django.template.context_processors.csrf',
                "django.template.context_processors.request",
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',

    'django.contrib.admindocs.middleware.XViewMiddleware',
    'fnp_django_pagination.middleware.PaginationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'fnpdjango.auth_backends.AttrCASBackend',
)

ROOT_URLCONF = 'redakcja.urls'

FIREPYTHON_LOGGER_NAME = "fnp"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'raven.contrib.django.raven_compat',

    'sorl.thumbnail',
    'fnp_django_pagination',
    'django_gravatar',
    'fileupload',
    'kombu.transport.django',
    'pipeline',
    'fnpdjango',

    'catalogue',
    'cover',
    'dvcs',
    'wiki',
    'wiki_img',
    'toolbar',
    'apiclient',
    'email_mangler',
)

LOGIN_REDIRECT_URL = '/documents/user'

CAS_USER_ATTRS_MAP = {
    'email': 'email', 'firstname': 'first_name', 'lastname': 'last_name'}

IMAGE_DIR = 'images/'


BROKER_URL = 'django://'
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_ACCEPT_CONTENT = ['pickle']  # Remove when all tasks jsonable.

SHOW_APP_VERSION = False

MIN_COVER_SIZE = (915, 1270)

try:
    from redakcja.settings.compress import *
except ImportError:
    pass

