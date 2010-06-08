#!/usr/bin/env python
from django.core.management import execute_manager

import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
sys.path += [os.path.realpath(os.path.join(*x)) for x in (
        (PROJECT_ROOT, '..'),
        (PROJECT_ROOT, '..', 'apps'),
        (PROJECT_ROOT, '..', 'lib')
)]

try:
    import localsettings  # Assumed to be in the same directory.
except ImportError:
    logging.exception("Failed to import settings")
    import sys
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(localsettings)
