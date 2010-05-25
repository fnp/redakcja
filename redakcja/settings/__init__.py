from __future__ import absolute_import
from settings.common import *

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_ROOT + '/dev.sqlite'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

try:
    from localsettings import *
except ImportError:
    pass

try:
    LOGGING_CONFIG_FILE
except NameError:
    LOGGING_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config',
                                ('logging.cfg' if not DEBUG else 'logging.cfg.dev'))
try:
    import logging

    if os.path.isfile(LOGGING_CONFIG_FILE):
        import logging.config
        logging.config.fileConfig(LOGGING_CONFIG_FILE)
    else:
        import sys
        logging.basicConfig(stream=sys.stderr)
except (ImportError,), exc:
    raise

