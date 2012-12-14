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

fixed = {}

tag_with_name = r"<([^>]+)name=\"([^>]+)>"

def fix(book, author, dry_run=True):
    if len(book) == 0:
        print "%s ==> does not contain chunks" % book.slug
        return
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
    fix(b, me, dry_run)

    
    
