# -*- coding: utf-8 -*-
from os import path

PROJECT_ROOT = path.realpath(path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    (u'Marek Stępniowski', 'marek@stepniowski.com'),
    (u'Łukasz Rekucki', 'lrekucki@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_ROOT + '/dev.sqlite'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw Poland'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'

#import locale
#locale.setlocale(locale.LC_ALL, '')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/'
STATIC_ROOT = PROJECT_ROOT + '/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ife@x^_lak+x84=lxtr!-ur$5g$+s6xt85gbbm@e_fk6q3r8=+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "explorer.context_processors.settings",
    "django.core.context_processors.request",
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'explorer.middleware.EditorSettingsMiddleware',
    'django.middleware.doc.XViewMiddleware',

    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates',
)

# CSS and JS files to compress
# COMPRESS_CSS = {
#     'all': {
#         'source_filenames': ('css/master.css', 'css/jquery.date_input.css', 'css/jquery.countdown.css',),
#         'output_filename': 'css/all.min.css',
#     }
# }
# 
# COMPRESS_JS = {
#     'all': {
#         'source_filenames': ('js/jquery.js', 'js/jquery.date_input.js', 'js/jquery.date_input-pl.js',
#             'js/jquery.countdown.js', 'js/jquery.countdown-pl.js',),
#         'output_filename': 'js/all.min.js',
#     }
# }
# 
# COMPRESS_CSS_FILTERS = None

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'piston',
    'sorl.thumbnail',
    'filebrowser',
    'explorer',
    'toolbar',
    'api',
)


FILEBROWSER_URL_FILEBROWSER_MEDIA = STATIC_URL + 'filebrowser/'
FILEBROWSER_DIRECTORY = 'images/'
FILEBROWSER_ADMIN_VERSIONS = []
FILEBROWSER_VERSIONS_BASEDIR = 'thumbnails/'

# REPOSITORY_PATH = '/Users/zuber/Projekty/platforma/files/books'
IMAGE_DIR = 'images'
EDITOR_COOKIE_NAME = 'options'
EDITOR_DEFAULT_SETTINGS = {
    'panels': [
        {'name': 'htmleditor', 'ratio': 0.5},
        {'name': 'gallery', 'ratio': 0.5}
    ],
}

# Python logging settings
import logging

log = logging.getLogger('platforma')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


# Import localsettings file, which may override settings defined here
try:
    from localsettings import *
except ImportError:
    pass

