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

datepd = r"(<dc:date.pd[^>]+>)([0-9]+)(</dc:date.pd>)"
def fix(book, author, dry_run=True):
    if len(book) == 0:
        print "%s does not contain chunks" % book.slug
        return
    fc = book[0]
    txt = fc.materialize()

    if dry_run:
        m = re.search(datepd, txt)
        if m:
            print("%s: %s->%d" % (book.slug, m.groups()[1], int(m.groups()[1])+70))
        else:
            print("%s: date.pd not found??" % (book.slug,))
    else:
        dates = {}
        def up_date(match):
            tagopen, date, tagclose = match.groups()
            olddate=date
            date = str(int(date)+70)
            dates['date'] = date
            dates['olddate'] = olddate
            return tagopen+date+tagclose
        new_txt = re.sub(datepd, up_date, txt)
        print "%s: %s->%s" % (book.slug, dates['olddate'], dates['date'])
        fc.commit(new_txt, author=author, description=u"Automatyczne poprawienie daty przejścia do domeny publicznej z %s na %s" % (dates['olddate'], dates['date']))

import sys
import getopt
from django.contrib.auth.models import User
opts, oth_ = getopt.getopt(sys.argv[1:],[],[ "seriously"])
dry_run = not (("--seriously",'') in opts)
me = User.objects.get(username='marcinkoziej')
if dry_run:
    print "This is a dry run, to really change dates, run with --seriously"
for b in Book.objects.all():
    fix(b, me, dry_run)

    
    
