# -*- coding: utf-8 -*-
from slughifi import slughifi
from collections import defaultdict
import json
from optparse import make_option
import urllib2

from py_etherpad import EtherpadLiteClient
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.db import transaction
from librarian.dcparser import BookInfo
from librarian import ParseError, ValidationError, WLURI
from django.conf import settings
from catalogue.models import Book
from catalogue.management import auto_taggers


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Less output'),
        make_option('-p', '--pad', dest='pad_id', help='Pad Id (or many id\'s, comma separated)'),
        make_option('-P', '--pad-ids', dest='pad_ids_file', help='Read Pad id\'s from file'),
        make_option('-E', '--edumed', dest="tag_edumed", default=False,
                    action='store_true', help="Perform EduMed pre-tagging"),
        make_option('-a', '--autotagger', dest="auto_tagger", default=None, help="Use auto-tagger (one of: %s)" % ', '.join(auto_taggers.keys())),
    )
    help = 'Imports Text files from EtherPad Lite.'

    def handle(self, *args, **options):

        self.style = color_style()

        verbose = options.get('verbose')
        pad_ids_file = options.get('pad_ids_file')
        if pad_ids_file:
            pad_id = open(pad_ids_file).readlines()
        else:
            pad_id = options.get("pad_id").split(',')
        pad_id = map(str.strip, pad_id)

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        if verbose:
            print 'Reading currently managed files (skipping hidden ones).'
        slugs = defaultdict(list)
        for b in Book.objects.exclude(slug__startswith='.').all():
            if verbose:
                print b.slug
            text = b.materialize().encode('utf-8')
            try:
                info = BookInfo.from_string(text)
                slugs[info.url.slug].append(b)
            except (ParseError, ValidationError):
                slugs[b.slug].append(b)

        book_count = 0
        commit_args = {
            "author_name": 'Platforma',
            "description": 'Automatycznie zaimportowane z EtherPad',
            "publishable": False,
        }

        if verbose:
            print 'Opening Pad'
        pad = EtherpadLiteClient(settings.ETHERPAD_APIKEY, settings.ETHERPAD_URL)

        for pid in pad_id:
            try:
                text = pad.getText(pid)['text']
            except ValueError:
                print "pad '%s' does not exist" % pid
                continue
            slug = slughifi(pid)
            print "Importing %s..." % pid
            title = pid

            print slugs, slug
            previous_books = slugs.get(slug)
            if previous_books:
                if len(previous_books) > 1:
                    print self.style.ERROR("There is more than one book "
                        "with slug %s:" % slug),
                previous_book = previous_books[0]
                comm = previous_book.slug
            else:
                previous_book = None
                comm = '*'
            print book_count, slug, '-->', comm

            if previous_book:
                book = previous_book
            else:
                book = Book()
                book.slug = slug
            book.title = title
            book.save()

            if len(book) > 0:
                chunk = book[0]
                chunk.slug = slug[:50]
                chunk.title = title[:255]
                chunk.save()
            else:
                chunk = book.add(slug, title)

            if options.get('tag_edumed'):
                auto_tagger = 'edumed'
            else:
                auto_tagger = options.get('auto_tagger')
            if auto_tagger:
                text = auto_taggers[auto_tagger](text)
            chunk.commit(text, **commit_args)

            book_count += 1

        # Print results
        print
        print "Results:"
        print "Imported %d books from Pad" % book_count

        transaction.commit()
        transaction.leave_transaction_management()
