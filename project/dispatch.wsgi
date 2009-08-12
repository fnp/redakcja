#!/usr/bin/env python
import os
from os import path
import sys

PROJECT_ROOT = path.realpath(path.dirname(__file__))

# Redirect sys.stdout to sys.stderr for bad libraries like geopy that use
# print statements for optional import exceptions.
sys.stdout = sys.stderr

# Add apps and lib directories to PYTHONPATH
sys.path.insert(0, path.join(PROJECT_ROOT, '../apps'))
sys.path.insert(0, path.join(PROJECT_ROOT, '../lib'))

# Emulate manage.py path hacking.
sys.path.insert(0, path.join(PROJECT_ROOT, ".."))
sys.path.insert(0, PROJECT_ROOT)

# Run Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

