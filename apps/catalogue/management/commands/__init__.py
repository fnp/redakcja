# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from catalogue.models import Book


class XmlUpdaterCommand(BaseCommand):
    """Base class for creating massive XML-updating commands.

    In a subclass, provide an XmlUpdater class in the `updater' attribute.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '-q', '--quiet', action='store_false', dest='verbose',
            default=True, help='Less output'),
        make_option(
            '-d', '--dry-run', action='store_true', dest='dry_run',
            default=False, help="Don't actually touch anything"),
        make_option(
            '-u', '--username', dest='username', metavar='USER',
            help='Assign commits to this user (required, preferably yourself).'),
    )
    args = "[slug]..."

    updater = NotImplemented

    def handle(self, *args, **options):
        verbose = options.get('verbose')
        dry_run = options.get('dry_run')
        username = options.get('username')

        if username:
            user = User.objects.get(username=username)
        else:
            print 'Please provide a username.'
            sys.exit(1)

        books = Book.objects.filter(slug__in=args) if args else None

        updater = self.updater()
        updater.run(user, verbose=verbose, dry_run=dry_run, books=books)
        updater.print_results()
