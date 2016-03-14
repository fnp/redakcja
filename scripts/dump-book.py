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

if len(sys.argv) != 3:
    print "dump-book slug-part filename"
    sys.exit(-1)

term = sys.argv[1]

books = Book.objects.filter(slug__contains=term)
if len(books) > 1:
    for b in range(len(books)):
        print "%d) %s" % (b+1, books[b].slug)
    print "Which one? "
    ch = int(raw_input())
    book = books[ch-1]
else:
    book = books[0]

open(sys.argv[2], "w").write(book.materialize().encode('utf-8'))

