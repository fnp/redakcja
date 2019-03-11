# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import csv

import sys
from django.contrib.auth.models import User
from lxml import etree
from collections import defaultdict
from django.core.management import BaseCommand

from catalogue.models import Book
from librarian import RDFNS, DCNS

CONTENT_TYPES = {
    'pdf':  'application/pdf',
    'epub': 'application/epub+zip',
    'mobi': 'application/x-mobipocket-ebook',
    'txt':  'text/plain',
    'html': 'text/html',
}


ISBN_TEMPLATES = (
    r'<dc:relation.hasFormat id="%(format)s" xmlns:dc="http://purl.org/dc/elements/1.1/">%(url)s'
    r'</dc:relation.hasFormat>',
    r'<meta refines="#%(format)s" id="%(format)s-id" property="dcterms:identifier">ISBN-%(isbn)s</meta>',
    r'<meta refines="#%(format)s-id" property="identifier-type">ISBN</meta>',
    r'<meta refines="#%(format)s" property="dcterms:format">%(content_type)s</meta>',
)


def url_for_format(slug, format):
    if format == 'html':
        return 'https://wolnelektury.pl/katalog/lektura/%s.html' % slug
    else:
        return 'http://wolnelektury.pl/media/book/%(format)s/%(slug)s.%(format)s' % {'slug': slug, 'format': format}


class Command(BaseCommand):
    args = 'csv_file'

    def add_arguments(self, parser):
        self.add_argument(
            '-u', '--username', dest='username', metavar='USER',
            help='Assign commits to this user (required, preferably yourself).')

    def handle(self, csv_file, **options):
        username = options.get('username')

        if username:
            user = User.objects.get(username=username)
        else:
            print('Please provide a username.')
            sys.exit(1)

        csvfile = open(csv_file, 'rb')
        isbn_lists = defaultdict(list)
        for slug, format, isbn in csv.reader(csvfile, delimiter=','):
            isbn_lists[slug].append((format, isbn))
        csvfile.close()

        for slug, isbn_list in isbn_lists.iteritems():
            print('processing %s' % slug)
            book = Book.objects.get(dc_slug=slug)
            chunk = book.chunk_set.first()
            old_head = chunk.head
            src = old_head.materialize()
            tree = etree.fromstring(src)
            isbn_node = tree.find('.//' + DCNS("relation.hasFormat"))
            if isbn_node is not None:
                print('%s already contains ISBN metadata, skipping' % slug)
                continue
            desc = tree.find(".//" + RDFNS("Description"))
            for format, isbn in isbn_list:
                for template in ISBN_TEMPLATES:
                    isbn_xml = template % {
                        'format': format,
                        'isbn': isbn,
                        'content_type': CONTENT_TYPES[format],
                        'url': url_for_format(slug, format),
                    }
                    element = etree.XML(isbn_xml)
                    element.tail = '\n'
                    desc.append(element)
            new_head = chunk.commit(
                etree.tostring(tree, encoding='unicode'),
                author=user,
                description='automatyczne dodanie isbn'
            )
            print('committed %s' % slug)
            if old_head.publishable:
                new_head.set_publishable(True)
            else:
                print('Warning: %s not publishable' % slug)
