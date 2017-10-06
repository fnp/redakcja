# -*- coding: utf-8 -*-

from optparse import make_option
from lxml import etree
import os

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.db import transaction

from catalogue.models import Book


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True, help='Less output'),
    )
    help = 'Imports XML files.'
    args = 'directory'

    def handle(self, directory, *args, **options):

        self.style = color_style()

        verbose = options.get('verbose')

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        book_count = 0
        commit_args = {
            "author_name": 'Platforma',
            "description": 'Automatycznie zaimportowane',
            "publishable": True,
        }
        for xml_filename in os.listdir(directory):
            if verbose:
                print xml_filename
            text = open(os.path.join(directory, xml_filename)).read().decode('utf-8')
            try:
                tree = etree.fromstring(text)
                slug = xml_filename.split('.')[0]
            except Exception as e:
                print xml_filename, 'error: ', repr(e)
            else:
                title = tree.find('.//header').text
                print book_count, slug, title
                Book.create(
                    text=text,
                    creator=None,
                    slug=slug,
                    title=title,
                    gallery=slug,
                    commit_args=commit_args,
                )
                book_count += 1

        # Print results
        print
        print "Results:"
        print "Imported %d books" % book_count
        print

        transaction.commit()
        transaction.leave_transaction_management()
