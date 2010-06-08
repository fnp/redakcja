from __future__ import with_statement

import shutil
import os
import sys
import logging

logging.basicConfig(stream=sys.stderr, format="%(levelname)s:: %(message)s", level=logging.INFO)

from string import Template

class DeploySite(object):

    def __init__(self, **env):
        self.env = env

        for arg in ('ROOT', 'PROJECT_NAME', 'PYTHON_VERSION'):
            if arg not in self.env:
                raise ValueError("Argument '%s' is required." % arg)

        if 'PYTHON_BASE' not in self.env:
            self.env['PYTHON_BASE'] = os.path.join(self.env['ROOT'], 'pythonenv')

        if 'PYTHON_BIN' not in self.env:
            self.env['PYTHON_BIN'] = os.path.join(
                        self.env['PYTHON_BASE'], 'bin', 'python') + self.env['PYTHON_VERSION']

        if 'PIP_BIN' not in self.env:
            self.env['PIP_BIN'] = os.path.join(self.env['PYTHON_BASE'], 'bin', 'pip')

        if 'PYTHON_SITE' not in self.env:
            self.env['PYTHON_SITE'] = os.path.join(
                        self.env['PYTHON_BASE'], 'lib',
                        'python' + self.env['PYTHON_VERSION'], 'site-packages')

        if 'APP_DIR' not in self.env:
            self.env['APP_DIR'] = os.path.join(self.env['ROOT'], 'application')

        if 'CONFIG_DIR' not in self.env:
            self.env['CONFIG_DIR'] = os.path.join(self.env['ROOT'], 'etc')

        if 'MEDIA_DIR' not in self.env:
            self.env['MEDIA_DIR'] = os.path.join(self.env['ROOT'], 'www', 'media')

        self._logger = logging.getLogger("deployment")

    def info(self, *args, **kwargs):
        self._logger.info(*args, **kwargs)

    def render_template(self, source, dest, extra_context={}):
        self.info("Rendering template: %s", source)

        with open(source, 'rb') as source_file:
            t = Template(source_file.read())

        context = dict(self.env)
        context.update(extra_context)

        with open(dest, 'wb') as dest_file:
            dest_file.write(t.safe_substitute(context))

        self.info("Done.")

    def restart_app(self):
        pass

    def update_app(self):
        pass

    def update_config(self):
        pass

    def install_dependencies(self):
        pass

    def deploy(self):
        self.update_app()
        self.install_dependencies()
        self.update_config()
        self.restart_app()

    def find_resource(self, path):
        for dir in (self.env['CONFIG_DIR'], self.env['APP_DIR']):
            full_path = os.path.join(dir, path)
            if os.path.isfile(full_path):
                return full_path

        raise ValueError("Resource '%s' not found" % path)

    @classmethod
    def run_deploy(cls, *args, **kwargs):
        site = cls(*args, **kwargs)
        return site.deploy()

class WSGISite(DeploySite):

    def __init__(self, **env):
        super(WSGISite, self).__init__(**env)

        if 'WSGI_FILE' not in self.env:
            self.env['WSGI_FILE'] = os.path.join(self.env['ROOT'], 'www',
                                        'wsgi', self.env['PROJECT_NAME']) + '.wsgi'

        self.env['WSGI_DIR'] = os.path.dirname(self.env['WSGI_FILE'])

        if 'WSGI_SOURCE_FILE' not in self.env:
            self.env['WSGI_SOURCE_FILE'] = 'wsgi_app.template'

        if 'WSGI_USER' not in self.env:
            self.env['WSGI_USER'] = 'www-data'

    def restart_app(self):
        self.info("Restarting wsgi application: %s", self.env['WSGI_FILE'])
        os.system("touch %s" % self.env['WSGI_FILE'])

    def update_config(self):
        super(WSGISite, self).update_config()

        source = self.find_resource(self.env['WSGI_SOURCE_FILE'])
        self.render_template(source, self.env['WSGI_FILE'])

class PIPSite(DeploySite):

    def install_dependencies(self):
        self.info("Installing requirements")
        os.system("%s install -r %s" % (self.env['PIP_BIN'], self.find_resource('requirements.txt')))

        try:
            self.info("Installing local requirements")
            os.system("%s install -r %s" % (self.env['PIP_BIN'], self.find_resource('requirements_local.txt')))
        except ValueError:
            pass

class GitSite(DeploySite):

    def update_app(self):
        self.info("Updating repository.")
        os.system("cd %s; git pull" % self.env['APP_DIR'])

class ApacheSite(DeploySite):

    def __init__(self, **env):
        super(ApacheSite, self).__init__(**env)

        if 'VHOST_SOURCE_FILE' not in self.env:
            self.env['VHOST_SOURCE_FILE'] = 'apache_vhost.template'

        if 'VHOST_FILE' not in self.env:
            self.env['VHOST_FILE'] = os.path.join(self.env['CONFIG_DIR'], self.env['PROJECT_NAME'] + '.vhost')

    def update_config(self):
        super(ApacheSite, self).update_config()

        source = self.find_resource(self.env['VHOST_SOURCE_FILE'])
        self.render_template(source, self.env['VHOST_FILE'])
