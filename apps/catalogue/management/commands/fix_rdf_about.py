# -*- coding: utf-8 -*-

from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from catalogue.models import Book


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose',
            default=True, help='Less output'),
        make_option('-d', '--dry-run', action='store_true', dest='dry_run',
            default=False, help="Don't actually touch anything"),
    )
    help = 'Updates the rdf:about metadata field.'

    def handle(self, *args, **options):
        from lxml import etree

        verbose = options.get('verbose')
        dry_run = options.get('dry_run')

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        all_books = 0
        nonxml = 0
        nordf = 0
        already = 0
        done = 0

        for b in Book.objects.all():
            all_books += 1
            if verbose:
                print "%s: " % b.title,
            chunk = b[0]
            old_head = chunk.head
            src = old_head.materialize()

            try:
                t = etree.fromstring(src)
            except:
                nonxml += 1
                if verbose:
                    print "invalid XML"
                continue
            desc = t.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
            if desc is None:
                nordf += 1
                if verbose:
                    print "no RDF found"
                continue

            correct_about = b.correct_about()
            attr_name = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
            if desc.get(attr_name) == correct_about:
                already += 1
                if verbose:
                    print "already correct"
                continue
            desc.set(attr_name, correct_about)
            if not dry_run:
                new_head = chunk.commit(etree.tostring(t, encoding=unicode),
                    author_name='platforma redakcyjna',
                    description='auto-update rdf:about'
                    )
                # retain the publishable status
                if old_head.publishable:
                    new_head.set_publishable(True)
            if verbose:
                print "done"
            done += 1

        # Print results
        print "All books: ", all_books
        print "Invalid XML: ", nonxml
        print "No RDF found: ", nordf
        print "Already correct: ", already
        print "Books updated: ", done

        transaction.commit()
        transaction.leave_transaction_management()

