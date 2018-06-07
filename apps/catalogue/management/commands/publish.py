# -*- coding: utf-8 -*-
import sys
from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    help = 'Publish lessons based on slugs in stdin'
    option_list = BaseCommand.option_list + (
        # make_option('-q', '--quiet', action='store_false', dest='verbose',
        #     default=True, help='Less output'),
        # make_option('-d', '--dry-run', action='store_true', dest='dry_run',
        #     default=False, help="Don't actually touch anything"),
        make_option(
            '-u', '--username', dest='username', metavar='USER',
            help='Assign commits to this user (required, preferably yourself).'),
    )

    def handle(self, *args, **options):
        user = User.objects.get(username=options.get('username'))
        slugs = [line.strip() for line in sys.stdin if line.strip()]
        for slug in slugs:
            lesson = Book.objects.get(slug=slug)
            print lesson.slug
            lesson.assert_publishable()
            lesson.publish(user)
