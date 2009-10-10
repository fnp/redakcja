from fabric.api import run, local, settings, abort, env, cd, require, abort

def staging():
    '''Use staging server'''
    env.hosts = ['platforma@stigma.nowoczesnapolska.org.pl:2222']
    env.project_dir = '/home/platforma/platforma'

def deploy():
    '''Deploy server'''
    require('project_dir', provided_by=['staging'])
    with cd(env.project_dir):
        run('git pull')
        run('./project/manage.py syncdb')
    restart_server()

def restart_server():
    with cd(env.project_dir):
        run('touch project/dispatch.wsgi')

