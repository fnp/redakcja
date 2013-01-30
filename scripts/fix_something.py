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
from lxml import etree

setup_environ(settings)

from catalogue.models import Book, Chunk
import re

fixed = {}

tag_with_name = r"<([^>]+)name=\"([^>]+)>"

def fix(book, author, dry_run=True):
    fc = book[0]
    txt = fc.materialize()

    newtxt, cnt = re.subn(tag_with_name, r'<\1nazwa="\2>', txt)
    if cnt == 0:
        print "%s ==> nothing changed" % book.slug
        return
    
    if not dry_run:
        print "%s ==> changing" % book.slug
        fc.commit(newtxt, author=author, description=u"Automatyczna zmiana atrybutu name na nazwa")
    else:
        print "%s ==> i would change this" % book.slug

def fix_empty_opis(book, author, dry_run=True):
    fc = book[0]
    txt = fc.materialize()
    try:
        t = etree.fromstring(txt)
        empty_opis = t.xpath('//opis[not(node())]')
        empty_cwiczenie = t.xpath('//cwiczenie[not(node())]')
        
        if empty_opis:
            print "%s: opis/ x %d" % (book.slug, len(empty_opis))

        if empty_cwiczenie:
            print "%s: cwiczenie/ x %d" % (book.slug, len(empty_cwiczenie))

    except:
        print "%s didn't parse" % b.slug
        return

    

import sys
import getopt
from django.contrib.auth.models import User
opts, oth_ = getopt.getopt(sys.argv[1:],
    [],
    [ "seriously"])
dry_run = not (("--seriously",'') in opts)
me = User.objects.get(username='marcinkoziej')
if dry_run:
    print "This is a dry run, to really fix something, run with --seriously"
for b in Book.objects.all():
    if len(b) == 0:
        print "%s ==> does not contain chunks" % b.slug
        continue
    fix_empty_opis(b, me, dry_run)

    
    
