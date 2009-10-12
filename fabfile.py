from __future__ import with_statement # needed for python 2.5
from fabric.api import *
from fabric.contrib.files import upload_template

import os


# ==========
# = Config =
# ==========
# Globals
env.project_name = 'platforma'
env.use_south = False

# Servers
def staging():
    """Use staging server"""
    env.hosts = ['stigma.nowoczesnapolska.org.pl:2222']
    env.user = 'zuber'
    env.path = '/var/services/platforma'
    env.python = '/usr/bin/python'
    env.virtualenv = '/usr/bin/virtualenv'
    env.pip = '/usr/bin/pip'
    
def production():
    """Use production server"""
    env.hosts = ['wolnelektury.pl:22123']
    env.user = 'fundacja'
    env.path = '/opt/lektury/platforma'
    env.python = '/opt/lektury/basevirtualenv/bin/python'
    env.virtualenv = '/opt/lektury/basevirtualenv/bin/virtualenv'
    env.pip = '/opt/lektury/basevirtualenv/bin/pip'


# =========
# = Tasks =
# =========
def test():
    "Run the test suite and bail out if it fails"
    require('hosts', 'path', provided_by=[staging, production])
    result = run('cd %(path)s/%(project_name)s; %(python)s manage.py test' % env)

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment. virtualenv and pip should be already installed.
    """
    require('hosts', 'path', provided_by=[staging, production])

    run('mkdir -p %(path)s; cd %(path)s; %(virtualenv)s --no-site-packages .;' % env, pty=True)
    run('cd %(path)s; mkdir releases; mkdir shared; mkdir packages;' % env, pty=True)
    run('cd %(path)s/releases; ln -s . current; ln -s . previous' % env, pty=True)
    deploy()

def deploy():
    """
    Deploy the latest version of the site to the servers, 
    install any required third party modules, 
    install the virtual host and then restart the webserver
    """
    require('hosts', 'path', provided_by=[staging, production])

    import time
    env.release = time.strftime('%Y-%m-%dT%H%M')

    upload_tar_from_git()
    upload_pybundle()
    install_requirements()
    upload_wsgi_script_sample()
    symlink_current_release()
    migrate()
    restart_webserver()

def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', 'path', provided_by=[localhost,webserver])
    env.version = version
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;', pty=True)
        run('ln -s %(version)s releases/current' % env, pty=True)
    restart_webserver()

def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[staging, production])
    require('path')
    with cd(env.path):
        run('mv releases/current releases/_previous;', pty=True)
        run('mv releases/previous releases/current;', pty=True)
        run('mv releases/_previous releases/previous;', pty=True)
    restart_webserver()


# =====================================================================
# = Helpers. These are called by other functions rather than directly =
# =====================================================================
def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it"
    print '>>> upload tar from git'
    require('release', provided_by=[deploy])
    local('git archive --format=tar master | gzip > %(release)s.tar.gz' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env, pty=True)
    run('mkdir -p %(path)s/packages' % env, pty=True)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env, pty=True)
    local('rm %(release)s.tar.gz' % env)

def install_requirements():
    "Install the required packages from the requirements file using pip"
    print '>>> install requirements'
    require('release', provided_by=[deploy])
    run('cd %(path)s; %(pip)s install -E . requirements.pybundle' % env)

def upload_pybundle():
    "Create pybundle with required libraries and upload it"
    print ">>> upload pybundle"
    require('release', provided_by=[deploy])
    with settings(warn_only=True):
        pip_options = run('cat %(path)s/releases/%(release)s/pip-options.txt' % env)
        if pip_options.failed:
            env.pip_options = ''
        else:
            env.pip_options = pip_options
            
    requirements_mtime = os.path.getmtime('requirements.txt')
    bundle_mtime = 0
    try:
        bundle_mtime = os.path.getmtime('requirements.pybundle')
    except os.error:
        pass

    if requirements_mtime > bundle_mtime:
        local('pip bundle requirements.pybundle %(pip_options)s -r requirements.txt' % env)
        put('requirements.pybundle', '%(path)s' % env)

def upload_wsgi_script_sample():
    "Create and upload a wsgi script sample"
    print ">>> upload wsgi script sample"
    print dict(env)
    upload_template('%(project_name)s.wsgi.template' % env, '%(path)s/%(project_name)s.wsgi.sample' % env, context=env)

def symlink_current_release():
    "Symlink our current release"
    print '>>> symlink current release'
    require('release', provided_by=[deploy])
    require('path', provided_by=[staging, production])
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous')
        run('ln -s %(release)s releases/current' % env)

def migrate():
    "Update the database"
    print '>>> migrate'
    require('project_name', provided_by=[staging, production])
    with cd('%(path)s/releases/current/%(project_name)s' % env):
        run('../../../bin/python manage.py syncdb --noinput' % env, pty=True)
        if env.use_south:
            run('../../../bin/python manage.py migrate' % env, pty=True)

def restart_webserver():
    "Restart the web server"
    print '>>> restart webserver'
    run('touch %(path)s/releases/current/%(project_name)s/%(project_name)s.wsgi' % env)
