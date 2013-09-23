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
from getopt import getopt

setup_environ(settings)

from catalogue.models import Book, Chunk
import re

from django.db import transaction

me = None

def books_by_slug(term, just_one=False, exclude=None):
    books = Book.objects.filter(slug__contains=term)
    if exclude:
        books = filter(lambda not b.slug in exclude, books)
    def show_them():
        for b in range(len(books)):
            print "%d) %s" % (b+1, books[b].slug)

    if just_one:
        if len(books) > 1:
            show_them()
            print "Which one? "
            ch = int(raw_input())
            book = books[ch-1]
        else:
            book = books[0]
        return book
    else:
        show_them()
        print "Is this ok? "
        ch = raw_input()
        if ch[0] in ('y', 'Y'):
            return books
        else:
            raise Exception("please change your query then")

def looks_good(book):
    for c in book:
        print "%02d. %s [%s]" % (c.number, c.title, c.slug)
    while True:
        print "is this ok (y/n)? "
        resp = raw_input()
        if resp[0] == 'y':
            break
        elif resp[0] == 'n':
            raise Exception("Aborting")


def move_chunk(term, chunk_idx, new_position):
    with transaction.commit_on_success():
        books = Book.objects.filter(slug__contains=term)
        book = books_by_slug(term, just_one=True)

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
        looks_good(book)

def append_chunks(books_slug, dest_slug, opts={}):
    inherit_slug = opts.has_key('-S')
    with transaction.commit_on_success():
        print "Choose destination:"
        dest = books_by_slug(dest_slug, just_one=opts.has_key('-A'))
        print "Choose source(s)"
        bookl = books_by_slug(books_slug, just_one=False, exclude=set(dest.slug))
        last = dest[len(dest)-1]
        for b in bookl:
            if b.id == dest.id: continue
            print "Appending %s (%s)" % (b.title, b.slug)
            for c in b:
                print "Appending %s (%s)" % (c.title, c.slug)
                last = last.split(inherit_slug and b.slug or c.slug, 
                                  inherit_slug and b.title or c.title)
                last.commit(c.materialize(), None,
                            author_name=opts['user_name'],
                            author_email=opts['user_email'])
        looks_good(dest)
                

DEFAULT_USER='marcinkoziej'

if __name__ == '__main__':
    opts, args = getopt(sys.argv[1:], "ma:Au:S")
    opdic = dict(opts)

#    opts['me'] = User.objects.get(username=opts.get('u', DEFAULT_USER))
    opdic['user_name'] = opdic.get('-U', 'Redakcja FNP')
    opdic['user_email'] = opdic.get('-E', 'redakcja@nowoczesnapolska.org.pl')
    if opdic.has_key('-m'):
        move_chunk(*args)
        sys.exit(0)
    elif opdic.has_key('-a'):
        dest_slug = opdic['-a']
        books_slug = args[0]
        append_chunks(books_slug, dest_slug, opdic)
    else:
        print "-m for move, -a for append"
        sys.exit(-1)
