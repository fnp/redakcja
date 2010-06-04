#!/srv/library/redakcja/pythonenv/bin/python
from __future__ import with_statement

import shutil
import os
import sys

from string import Template

def render_template(source, dest, context={}):
    print "Rendering template:",
    with open(source, 'rb') as source_file:
        t = Template(source_file.read())
    with open(dest, 'wb') as dest_file:
        dest_file.write(t.safe_substitute(context))
    print "done."

def restart_wsgi():
    print "Restarting wsgi application:",
    os.system("touch %s" % WSGI_TARGET)
    print "done."

def update_application():
    print "Updating repository.",
    os.system("cd %s; git pull" % PROJECT_ROOT)
    print "Installing requirements"
    os.system("pip install -r %s" % os.path.join(PROJECT_ROOT, 'requirements.txt'))
    print "Installing local requirements"
    os.system("pip install -r %s" % os.path.join(ROOT, 'etc', 'requirements.txt'))
    print "done."


PYTHON = os.path.join(ROOT, 'pythonenv', 'bin', 'python')
PYTHON_SITE = os.path.join(ROOT, 'pythonenv', 'lib', 'python2.6', 'site-packages')

PROJECT_NAME = 'redakcja'
PROJECT_ROOT = os.path.join(ROOT, 'application')

MEDIA_ROOT = os.path.join(ROOT, 'www', 'media')

ADMIN_EMAIL = 'lrekucki@gmail.com'

WSGI_TARGET = os.path.join(ROOT, 'www', 'wsgi', PROJECT_NAME + '.wsgi')
WSGI_DIR = os.path.dirname(WSGI_TARGET)

WSGI_USER = PROJECT_NAME
WSGI_PROCESSES = 5
WSGI_THREADS = 1

DOMAIN = 'redakcja.wolnelektury.pl'
DOMAIN_ALIASES = 'redakcja.nowoczesnapolska.org.pl'

#
# Load local configuration
#
sys.path = [ os.path.join(ROOT, 'etc') ] + sys.path

from local_deployment import *

if __name__ == '__main__':
    update_application()
    render_template(os.path.join(PROJECT_ROOT, PROJECT_NAME + '.wsgi.template'), WSGI_TARGET, context=globals())
    render_template(os.path.join(PROJECT_ROOT, PROJECT_NAME + '.vhost.template'), os.path.join(ROOT, 'etc', PROJECT_NAME + '.vhost'), context=globals())
    restart_wsgi()
