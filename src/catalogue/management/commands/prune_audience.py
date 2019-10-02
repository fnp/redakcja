# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
from django.contrib.auth.models import User
from lxml import etree

from django.core.management import BaseCommand

from catalogue.models import Book
from librarian import DCNS


class Command(BaseCommand):
    args = 'exclude_file'

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--username', dest='username', metavar='USER',
            help='Assign commits to this user (required, preferably yourself).')

    def handle(self, exclude_file, **options):
        username = options.get('username')

        if username:
            user = User.objects.get(username=username)
        else:
            print('Please provide a username.')
            sys.exit(1)

        excluded_slugs = [line.strip() for line in open(exclude_file, 'rb') if line.strip()]
        books = Book.objects.exclude(slug__in=excluded_slugs)

        for book in books:
            if not book.is_published():
                continue
            print('processing %s' % book.slug)
            chunk = book.chunk_set.first()
            old_head = chunk.head
            src = old_head.materialize()
            tree = etree.fromstring(src)
            audience_nodes = tree.findall('.//' + DCNS("audience"))
            if not audience_nodes:
                print('%s has no audience, skipping' % book.slug)
                continue

            for node in audience_nodes:
                node.getparent().remove(node)

            chunk.commit(
                etree.tostring(tree, encoding='unicode'),
                author=user,
                description='automatyczne skasowanie audience',
                publishable=old_head.publishable
            )
            print('committed %s' % book.slug)
            if not old_head.publishable:
                print('Warning: %s not publishable, last head: %s, %s' % (
                    book.slug, old_head.author.username, old_head.description[:40].replace('\n', ' ')))
