from fabric.api import run, env, cd

def staging():
    '''Add staging server to hosts'''
    env.hosts += ['platforma@stigma.nowoczesnapolska.org.pl:2222']

def deploy():
    '''Deploy server'''
    with cd('platforma'):
        run('git pull')
        run('./project/manage.py syncdb')
