# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
from subprocess import call
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--node-bin-path',
            action='store',
            dest='node_bin_path',
            default=None,
            help='Path to node binary')
        parser.add_argument(
            '--npm-bin',
            action='store',
            dest='npm_bin',
            default='npm',
            help='Path to npm binary')
        parser.add_argument(
            '--editor-npm-env',
            action='store',
            dest='editor_npm_env',
            default=None,
            help='Destination path of npm environment, defaults to ./node_modules')
        parser.add_argument(
            '--editor-optimize',
            action='store',
            dest='editor_optimize',
            default=None,
            help='Optimization strategy for editor build')

    def handle(self, **options):
        wiki_base_dir = os.path.join(os.getcwd(), 'apps', 'wiki', 'static', 'wiki')
        rng_base_dir = os.path.join(wiki_base_dir, 'editor')
        build_dir = os.path.join(wiki_base_dir, 'build')

        self.stdout.write('Installing editor dependencies')
        if options['editor_npm_env']:
            npm_env = os.path.join(rng_base_dir, options['editor_npm_env'])
            if not os.path.exists(npm_env):
                os.makedirs(npm_env)
            assert os.path.isdir(npm_env)
            os.symlink(npm_env, os.path.join(rng_base_dir, 'node_modules'))
        try:
            call([options['npm_bin'], 'install'], cwd=rng_base_dir)
        except OSError:
            raise CommandError('Something went wrong, propably npm binary not found. Tried: %s' % options['npm_bin'])

        self.stdout.write('Building editor')
        if options['node_bin_path']:
            # grunt needs npm binary to be foundable in PATH
            os.environ['PATH'] = '%s:%s' % (options['node_bin_path'], os.environ['PATH'])
        args = ['./node_modules/.bin/grunt', 'build', '--output-dir=%s' % build_dir]
        if options['editor_optimize']:
            args.append('--optimize=%s' % options['editor_optimize'])
        self.stdout.write('Calling %s at %s' % (' '.join(args), rng_base_dir))
        call(args, cwd=rng_base_dir)

        call_command('collectstatic', interactive=False, ignore_patterns=['editor'])
