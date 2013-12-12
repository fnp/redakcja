import os
from subprocess import call
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--node-bin-path',
            action='store',
            dest='node_bin_path',
            type='string',
            default=None,
            help='Path to node binary'),
        make_option('--npm-bin',
            action='store',
            dest='npm_bin',
            type='string',
            default='npm',
            help='Path to npm binary'),
        )

    def handle(self, **options):
        wiki_base_dir = os.path.join(os.getcwd(), 'apps', 'wiki', 'static', 'wiki')
        rng_base_dir = os.path.join(wiki_base_dir, 'rng')
        build_dir = os.path.join(wiki_base_dir, 'build')

        self.stdout.write('Installing editor dependencies')
        try:
            call([options['npm_bin'], 'install'], cwd = rng_base_dir)
        except OSError:
            raise CommandError('Something went wrong, propably npm binary not found. Tried: %s' % options['npm_bin'])

        self.stdout.write('Building editor')
        if options['node_bin_path']:
            # grunt needs npm binary to be foundable in PATH
            os.environ['PATH'] = '%s:%s' % (options['node_bin_path'], os.environ['PATH'])
        call(['./node_modules/.bin/grunt', 'build', '--output-dir=%s' % build_dir], cwd = rng_base_dir)

        call_command('collectstatic', interactive = False, ignore_patterns = ['rng'])
