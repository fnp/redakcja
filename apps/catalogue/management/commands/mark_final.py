# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
from django.contrib.auth.models import User
from optparse import make_option

from collections import defaultdict
from django.core.management import BaseCommand

from catalogue.models import Book, Chunk


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        # make_option('-q', '--quiet', action='store_false', dest='verbose',
        #     default=True, help='Less output'),
        # make_option('-d', '--dry-run', action='store_true', dest='dry_run',
        #     default=False, help="Don't actually touch anything"),
        make_option(
            '-u', '--username', dest='username', metavar='USER',
            help='Assign commits to this user (required).'),
    )
    args = 'slug_file'

    def handle(self, slug_file, **options):
        username = options.get('username')

        if username:
            user = User.objects.get(username=username)
        else:
            print 'Please provide a username.'
            sys.exit(1)

        slugs = [line.strip() for line in open(slug_file)]
        books = Book.objects.filter(slug__in=slugs)

        for book in books:
            print 'processing %s' % book.slug
            chunk = book.chunk_set.first()
            src = chunk.head.materialize()
            chunk.commit(
                text=src,
                author=user,
                description=u'Ostateczna akceptacja merytoryczna przez kierownika literackiego.',
                tags=[Chunk.tag_model.objects.get(slug='editor-proofreading')],
                publishable=True
            )
            print 'committed %s' % book.slug
