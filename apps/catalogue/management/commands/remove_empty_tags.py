# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
from django.contrib.auth.models import User
from optparse import make_option

from django.core.management import BaseCommand

from catalogue.models import Book
from catalogue.xml_tools import remove_empty_elements

EXCLUDED_SLUGS = [
    'aktualizacja-szablonu-8kwie',
]


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        # make_option('-q', '--quiet', action='store_false', dest='verbose',
        #     default=True, help='Less output'),
        # make_option('-d', '--dry-run', action='store_true', dest='dry_run',
        #     default=False, help="Don't actually touch anything"),
        make_option(
            '-u', '--username', dest='username', metavar='USER',
            help='Assign commits to this user (required, preferably yourself).'),
    )

    def handle(self, **options):
        username = options.get('username')

        if username:
            user = User.objects.get(username=username)
        else:
            print 'Please provide a username.'
            sys.exit(1)

        for book in Book.objects.all():
            if book.slug in EXCLUDED_SLUGS:
                continue
            print 'processing %s' % book.slug
            for chunk in book.chunk_set.all():
                old_head = chunk.head
                src = old_head.materialize()
                new_xml = remove_empty_elements(src)
                if new_xml:
                    new_head = chunk.commit(
                        new_xml,
                        author=user,
                        description=u'automatyczne usunięcie pustych znaczników'
                    )
                    print 'committed %s (chunk %s)' % (book.slug, chunk.number)
                    if old_head.publishable:
                        new_head.set_publishable(True)
