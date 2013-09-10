#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
sys.path.append('.')
sys.path.append('./apps')
sys.path.append('./lib')

from django.core.management import setup_environ
from redakcja import settings

setup_environ(settings)

from catalogue.models import Book, Chunk
import re

from django.db import transaction

if len(sys.argv) != 4:
    print "dump-book slug-part chunk-no to-position"
    sys.exit(-1)

term = sys.argv[1]
chunk_idx = int(sys.argv[2])
new_position = int(sys.argv[3])

with transaction.commit_on_success():
    books = Book.objects.filter(slug__contains=term)
    if len(books) > 1:
        for b in range(len(books)):
            print "%d) %s" % (b+1, books[b].slug)
        print "Which one? "
        ch = int(raw_input())
        book = books[ch-1]
    else:
        book = books[0]

    chunks_total = len(book)
    max_number = max(c.number for c in book)
    moving_chunk = next(c for c in book if c.number == chunk_idx)

    moving_chunk.number = max_number+2
    moving_chunk.save()

    adjust = 1
    for i in range(chunks_total-1, -1, -1):
        chunk = book[i]
        chunk.number = i + 1 + adjust
        chunk.save()
        if i + 1 == new_position:
            adjust = 0


    moving_chunk.number = new_position
    moving_chunk.save()

    book = Book.objects.get(pk=book.pk)
    for c in book:
        print c
    while True:
        print "is this ok (y/n)? "
        resp = raw_input()
        if resp[0] == 'y':
            break
        elif resp[0] == 'n':
            raise Exception("Aborting")
    

