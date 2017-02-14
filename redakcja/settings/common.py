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
LANGUAGE_CODE = 'en'

# import locale
# locale.setlocale(locale.LC_ALL, '')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True
LANGUAGES = [
    ('en', 'English'),
    ('pl', 'polski'),
]

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/dynamic'
STATIC_ROOT = PROJECT_ROOT + '/../static/'

STATICFILES_DIRS = [
    PROJECT_ROOT + '/static/'
]

LOCALE_PATHS = [
    PROJECT_ROOT + '/locale/',
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
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "redakcja.context_processors.settings",  # this is instead of media
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
    'django.middleware.locale.LocaleMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django_cas.middleware.CASMiddleware',

    'django.contrib.admindocs.middleware.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    # 'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
#     'fnpdjango.auth_backends.AttrCASBackend',
# )

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
    'django.contrib.flatpages',
    # 'django.contrib.comments',

    # 'south',
    'sorl.thumbnail',
    'pagination',
    # 'gravatar',
    # 'kombu.transport.django',
    'fileupload',
    'pipeline',
    'modeltranslation',
    'constance',
    'constance.backends.database',

    'catalogue',
    # 'cover',
    'dvcs',
    'organizations',
    'wiki',
    # 'toolbar',
    # 'apiclient',
    'email_mangler',
    'build',
    'attachments',

    'django_forms_bootstrap',
    'forms_builder.forms',
    'fnpdjango',
)

LOGIN_REDIRECT_URL = '/'

# CAS_USER_ATTRS_MAP = {
#     'email': 'email', 'firstname': 'first_name', 'lastname': 'last_name'}

# REPOSITORY_PATH = '/Users/zuber/Projekty/platforma/files/books'

IMAGE_DIR = 'images/'


# import djcelery
# djcelery.setup_loader()

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

SHOW_APP_VERSION = False


FORMS_BUILDER_EDITABLE_SLUGS = True
FORMS_BUILDER_LABEL_MAX_LENGTH = 2048


try:
    from redakcja.settings.compress import *
except ImportError:
    pass
