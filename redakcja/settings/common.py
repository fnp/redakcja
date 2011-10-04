# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path

PROJECT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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
STATIC_ROOT = PROJECT_ROOT + '/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/dynamic/'
STATIC_URL = '/media/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ife@x^_lak+x84=lxtr!-ur$5g$+s6xt85gbbm@e_fk6q3r8=+'
SESSION_COOKIE_NAME = "redakcja_sessionid"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "redakcja.context_processors.settings", # this is instead of media
    'django.core.context_processors.csrf',
    "django.core.context_processors.request",
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',

    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)

ROOT_URLCONF = 'redakcja.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates',
)

FIREPYTHON_LOGGER_NAME = "fnp"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',

    'compress',
    'south',
    'sorl.thumbnail',
    'filebrowser',
    'pagination',
    'gravatar',
    'djcelery',
    'djkombu',

    'catalogue',
    'dvcs',
    'wiki',
    'toolbar',
    'apiclient',
)

LOGIN_REDIRECT_URL = '/documents/user'


FILEBROWSER_URL_FILEBROWSER_MEDIA = STATIC_URL + 'filebrowser/'
FILEBROWSER_DIRECTORY = 'images/'
FILEBROWSER_ADMIN_VERSIONS = []
FILEBROWSER_VERSIONS_BASEDIR = 'thumbnails/'
FILEBROWSER_DEFAULT_ORDER = "path_relative"

# REPOSITORY_PATH = '/Users/zuber/Projekty/platforma/files/books'
IMAGE_DIR = 'images'


import djcelery
djcelery.setup_loader()

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

SHOW_APP_VERSION = False

try:
    from redakcja.settings.compress import *
except ImportError:
    pass

