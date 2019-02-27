# -*- coding: utf-8 -*-

import csv
from optparse import make_option
import re
import sys
import urllib
import urllib2

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.db import transaction

from slugify import slugify
from catalogue.models import Chunk


REDMINE_CSV = 'http://redmine.nowoczesnapolska.org.pl/projects/wl-publikacje/issues.csv'
REDAKCJA_URL = 'http://redakcja.wolnelektury.pl/documents/'


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-r', '--redakcja', dest='redakcja', metavar='URL',
            help='Base URL of Redakcja documents',
            default=REDAKCJA_URL),
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Less output'),
        make_option('-f', '--force', action='store_true', dest='force', default=False,
            help='Force assignment overwrite'),
    )
    help = 'Imports ticket assignments from Redmine.'
    args = '[redmine-csv-url]'

    def handle(self, *redmine_csv, **options):

        self.style = color_style()

        redakcja = options.get('redakcja')
        verbose = options.get('verbose')
        force = options.get('force')

        if not redmine_csv:
            if verbose:
                print "Using default Redmine CSV URL:", REDMINE_CSV
            redmine_csv = REDMINE_CSV

        # Start transaction management.
        transaction.enter_transaction_management()

        redakcja_link = re.compile(re.escape(redakcja) + r'([-_.:?&%/a-zA-Z0-9]*)')

        all_tickets = 0
        all_chunks = 0
        done_tickets = 0
        done_chunks = 0
        empty_users = 0
        unknown_users = {}
        unknown_books = []
        forced = []

        if verbose:
            print 'Downloading CSV file'
        for r in csv.reader(urllib2.urlopen(redmine_csv)):
            if r[0] == '#':
                continue
            all_tickets += 1

            username = r[6]
            if not username:
                if verbose:
                    print "Empty user, skipping"
                empty_users += 1
                continue

            first_name, last_name = unicode(username, 'utf-8').rsplit(u' ', 1)
            try:
                user = User.objects.get(first_name=first_name, last_name=last_name)
            except User.DoesNotExist:
                print self.style.ERROR('Unknown user: ' + username)
                unknown_users.setdefault(username, 0)
                unknown_users[username] += 1
                continue

            ticket_done = False
            for fname in redakcja_link.findall(r[-1]):
                fname = unicode(urllib.unquote(fname), 'utf-8', 'ignore')
                if fname.endswith('.xml'):
                    fname = fname[:-4]
                fname = fname.replace(' ', '_')
                fname = slugify(fname)

                chunks = Chunk.objects.filter(book__slug=fname)
                if not chunks:
                    print self.style.ERROR('Unknown book: ' + fname)
                    unknown_books.append(fname)
                    continue
                all_chunks += chunks.count()

                for chunk in chunks:
                    if chunk.user:
                        if chunk.user == user:
                            continue
                        else:
                            forced.append((chunk, chunk.user, user))
                            if force:
                                print self.style.WARNING(
                                    '%s assigned to %s, forcing change to %s.' %
                                    (chunk.pretty_name(), chunk.user, user))
                            else:
                                print self.style.WARNING(
                                    '%s assigned to %s not to %s, skipping.' %
                                    (chunk.pretty_name(), chunk.user, user))
                                continue
                    chunk.user = user
                    chunk.save()
                    ticket_done = True
                    done_chunks += 1

            if ticket_done:
                done_tickets += 1


        # Print results
        print
        print "Results:"
        print "Assignments imported from %d/%d tickets to %d/%d relevalt chunks." % (
                done_tickets, all_tickets, done_chunks, all_chunks)
        if empty_users:
            print "%d tickets were unassigned." % empty_users
        if forced:
            print "%d assignments conficts (%s):" % (
                len(forced), "changed" if force else "left")
            for chunk, orig, user in forced:
                print "  %s: \t%s \t->  %s" % (
                    chunk.pretty_name(), orig.username, user.username)
        if unknown_books:
            print "%d unknown books:" % len(unknown_books)
            for fname in unknown_books:
                print "  %s" % fname
        if unknown_users:
            print "%d unknown users:" % len(unknown_users)
            for name in unknown_users:
                print "  %s (%d tickets)" % (name, unknown_users[name])
        print


        transaction.commit()
        transaction.leave_transaction_management()

