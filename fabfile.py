from __future__ import with_statement

from fabric.api import run, env, cd

def staging():
    '''Add staging server to hosts'''
    env.hosts = ['platforma@stigma.nowoczesnapolska.org.pl:2222']
    env.project_dir = '/home/platforma/platforma'

def deploy():
    '''Deploy server'''
    with cd(env.project_dir):
        run('git pull')
        run('./project/manage.py syncdb')
    restart_server()

def restart_server():
    with cd(env.project_dir):
        run('touch project/dispatch.wsgi')

