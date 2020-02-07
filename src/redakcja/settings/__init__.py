# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os.path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from .defaults import *
from ..localsettings import *

DATA_UPLOAD_MAX_MEMORY_SIZE = 20000000

PROJECT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

STATICFILES_DIRS = [
    PROJECT_ROOT + '/static/'
]

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
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    ]

if CAS_SERVER_URL:
    MIDDLEWARE.append(
        'django_cas_ng.middleware.CASMiddleware',
    )

MIDDLEWARE += [
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'fnp_django_pagination.middleware.PaginationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
]

if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE

if CAS_SERVER_URL:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )

ROOT_URLCONF = 'redakcja.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'sorl.thumbnail',
    'fnp_django_pagination',
    'django_gravatar',
    'fileupload',
    'pipeline',
    'fnpdjango',
    'django_cas_ng',
    'bootstrap4',

    'catalogue',
    'cover',
    'dvcs',
    'wiki',
    'wiki_img',
    'toolbar',
    'apiclient',
    'email_mangler',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

LOGIN_REDIRECT_URL = '/documents/user'

MIN_COVER_SIZE = (915, 1270)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE = {
    'CSS_COMPRESSOR': None,
    'JS_COMPRESSOR': None,
    'COMPILERS': (
        'libsasscompiler.LibSassCompiler',
    ),

    # CSS and JS files to compress
    'STYLESHEETS': {
        'detail': {
            'source_filenames': (
                'css/master.css',
                'css/toolbar.css',
                'css/gallery.css',
                'css/history.css',
                'css/summary.css',
                'css/html.css',
                'css/imgareaselect-default.css',
                'css/dialogs.css',

                'wiki/scss/splitter.scss',
                'wiki/scss/visual.scss'
            ),
            'output_filename': 'compressed/detail_styles.css',
        },
        'catalogue': {
            'source_filenames': (
                'css/filelist.css',
            ),
            'output_filename': 'compressed/catalogue_styles.css',
        },
        'book': {
            'source_filenames': (
                'css/book.css',
            ),
            'output_filename': 'compressed/book.css',
        },
        'book_list': {
            'source_filenames': (
                'css/book_list.css',
            ),
            'output_filename': 'compressed/book_list.css',
        },
    },
    'JAVASCRIPT': {
        # everything except codemirror
        'detail': {
            'source_filenames': (
                # libraries
                'js/lib/jquery/jquery.blockui.js',
                'js/lib/jquery/jquery.elastic.js',
                'js/lib/jquery/jquery.xmlns.js',
                'js/button_scripts.js',
                'js/slugify.js',

                # wiki scripts
                'js/wiki/wikiapi.js',
                'wiki/js/themes.js',
                'js/wiki/xslt.js',

                # base UI
                'js/wiki/base.js',
                'wiki/js/sidebar-perspective.js',
                'js/wiki/toolbar.js',

                # dialogs
                'js/wiki/dialog_save.js',
                'js/wiki/dialog_revert.js',
                'js/wiki/dialog_pubmark.js',

                # views
                'js/wiki/view_history.js',
                'js/wiki/view_summary.js',
                'js/wiki/view_editor_source.js',
                'js/wiki/view_editor_wysiwyg.js',
                'js/wiki/view_gallery.js',
                'js/wiki/view_annotations.js',
                'js/wiki/view_search.js',
                'js/wiki/view_column_diff.js',
            ),
            'output_filename': 'compressed/detail_scripts.js',
        },
        'wiki_img': {
            'source_filenames': (
                # libraries
                'js/lib/jquery/jquery.blockui.js',
                'js/lib/jquery/jquery.elastic.js',
                'js/lib/jquery/jquery.imgareaselect.js',
                'js/button_scripts.js',
                'js/slugify.js',

                # wiki scripts
                'js/wiki_img/wikiapi.js',
                'wiki/js/themes.js',

                # base UI
                'js/wiki_img/base.js',
                'js/wiki/toolbar.js',

                # dialogs
                'js/wiki/dialog_save.js',
                'js/wiki/dialog_revert.js',
                'js/wiki/dialog_pubmark.js',

                # views
                'js/wiki_img/view_editor_objects.js',
                'js/wiki_img/view_editor_motifs.js',
                'js/wiki/view_editor_source.js',
                'js/wiki/view_history.js',
                'js/wiki/view_column_diff.js',
            ),
            'output_filename': 'compressed/detail_img_scripts.js',
        },
        'catalogue': {
            'source_filenames': (
                'js/catalogue/catalogue.js',
                'js/slugify.js',
                'email_mangler/email_mangler.js',
            ),
            'output_filename': 'compressed/catalogue_scripts.js',
        },
        'book': {
            'source_filenames': (
                'js/book_text/jquery.eventdelegation.js',
                'js/book_text/jquery.scrollto.js',
                'js/book_text/jquery.highlightfade.js',
                'js/book_text/book.js',
            ),
            'output_filename': 'compressed/book.js',
        },
        'book_list': {
            'source_filenames': (
                'js/catalogue/book_list.js',
            ),
            'output_filename': 'compressed/book_list.js',
        }
    }
}


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


try:
    SENTRY_DSN
except NameError:
    pass
else:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
