# -*- coding: utf-8 -*-

from collections import defaultdict
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
        transaction.enter_transaction_management()

        if verbose:
            print 'Reading currently managed files (skipping hidden ones).'
        slugs = defaultdict(list)
        for b in Book.objects.exclude(slug__startswith='.').all():
            if verbose:
                print b.slug
            text = b.materialize().encode('utf-8')
            try:
                info = BookInfo.from_bytes(text)
            except (ParseError, ValidationError):
                pass
            else:
                slugs[info.slug].append(b)

        book_count = 0
        commit_args = {
            "author_name": 'Platforma',
            "description": 'Automatycznie zaimportowane z Wolnych Lektur',
            "publishable": True,
        }

        if verbose:
            print 'Opening books list'
        for book in json.load(urllib2.urlopen(WL_API)):
            book_detail = json.load(urllib2.urlopen(book['href']))
            xml_text = urllib2.urlopen(book_detail['xml']).read()
            info = BookInfo.from_bytes(xml_text)
            previous_books = slugs.get(info.slug)
            if previous_books:
                if len(previous_books) > 1:
                    print self.style.ERROR("There is more than one book "
                        "with slug %s:"), 
                previous_book = previous_books[0]
                comm = previous_book.slug
            else:
                previous_book = None
                comm = '*'
            print book_count, info.slug , '-->', comm
            Book.import_xml_text(xml_text, title=info.title[:255],
                slug=info.slug[:128], previous_book=previous_book,
                commit_args=commit_args)
            book_count += 1

        # Print results
        print
        print "Results:"
        print "Imported %d books from WL:" % (
                book_count, )
        print


        transaction.commit()
        transaction.leave_transaction_management()

