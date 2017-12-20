# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json

import sys
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from lxml import etree
from optparse import make_option

from django.core.management import BaseCommand

from catalogue.models import Book
from librarian import DCNS

DC_TEMPLATE = r'<dc:subject.curriculum.new xmlns:dc="http://purl.org/dc/elements/1.1/">%s</dc:subject.curriculum.new>'


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
    args = 'csv_file'

    def handle(self, json_file, **options):
        username = options.get('username')

        if username:
            user = User.objects.get(username=username)
        else:
            print 'Please provide a username.'
            sys.exit(1)

        data = json.load(open(json_file, 'rb'))

        for slug, ident_list in data:
            print 'processing %s' % slug
            try:
                book = Book.objects.get(slug=slug)
            except Book.DoesNotExist:
                print 'WARNING %s not found!!!' % slug
                continue
            chunk = book.chunk_set.all()[0]
            old_head = chunk.head
            src = old_head.materialize()
            tree = etree.fromstring(force_str(src.replace('&nbsp;', u'\xa0')))
            curr_node = tree.find('.//' + DCNS("subject.curriculum.new"))
            if curr_node is not None:
                print '%s already contains new curriculum metadata, skipping' % slug
                continue
            desc = tree.find(".//metadata")
            for ident in ident_list:
                dc_xml = DC_TEMPLATE % ident
                element = etree.XML(dc_xml)
                element.tail = '\n'
                desc.append(element)
            new_head = chunk.commit(
                etree.tostring(tree, encoding=unicode),
                author=user,
                description='automatyczne dodanie nowej podstawy programowej'
            )
            print 'committed %s' % slug
            if old_head.publishable:
                new_head.set_publishable(True)
            else:
                print 'Warning: %s not publishable' % slug
