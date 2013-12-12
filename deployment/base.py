from fabric.api import env
from fabric.tasks import Task
from fnpdjango.deploy import Command


class Environment(Task):
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self.npm_bin = kwargs.pop('npm_bin', 'npm')
        self.host = kwargs.pop('host')
        self.env_vars = kwargs
        self.env_vars['skip_collect_static'] = True

    def run(self, *args, **kwargs):
        env.project_name = 'redakcja'
        env.hosts = [self.host]
        for k,v in self.env_vars.items():
            env[k] = v

        build_cmd = '../../ve/bin/python manage.py build --npm-bin=%s' % self.npm_bin
        if 'node_bin_path' in self.env_vars:
            build_cmd += ' --node-bin-path=%s' % self.env_vars['node_bin_path']

        env.pre_collectstatic = [
            Command([build_cmd], '')
        ]
