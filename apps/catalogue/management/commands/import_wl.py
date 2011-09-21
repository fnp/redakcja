# -*- coding: utf-8 -*-

import json
from optparse import make_option
import urllib2

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.db import transaction
from librarian.dcparser import BookInfo
from librarian import ParseError, ValidationError

from catalogue.models import Book


WL_API = 'http://www.wolnelektury.pl/api/books/'


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Less output'),
    )
    help = 'Imports XML files from WL.'

    def handle(self, *args, **options):

        self.style = color_style()

        verbose = options.get('verbose')

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        if verbose:
            print 'Reading currently managed files.'
        slugs = {}
        for b in Book.objects.all():
            if verbose:
                print b.slug
            text = b.materialize().encode('utf-8')
            try:
                info = BookInfo.from_string(text)
            except (ParseError, ValidationError):
                pass
            else:
                slugs[info.slug] = b

        book_count = 0
        commit_args = {
            "author_name": 'Platforma',
            "description": 'Import from WL',
        }

        if verbose:
            print 'Opening books list'
        for book in json.load(urllib2.urlopen(WL_API)):
            book_detail = json.load(urllib2.urlopen(book['href']))
            xml_text = urllib2.urlopen(book_detail['xml']).read()
            info = BookInfo.from_string(xml_text)
            previous_book = slugs.get(info.slug, None)
            if previous_book:
                comm = previous_book.slug
            else:
                comm = '*'
            print book_count, info.slug , '-->', comm
            Book.import_xml_text(xml_text, title=info.title,
                slug=info.slug, previous_book=slugs.get(info.slug, None))
            book_count += 1

        # Print results
        print
        print "Results:"
        print "Imported %d books from WL:" % (
                book_count, )
        print


        transaction.commit()
        transaction.leave_transaction_management()

