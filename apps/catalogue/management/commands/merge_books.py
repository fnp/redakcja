# -*- coding: utf-8 -*-

from optparse import make_option
import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.db import transaction

from slughifi import slughifi
from catalogue.models import Book


def common_prefix(texts):
    common = []

    min_len = min(len(text) for text in texts)
    for i in range(min_len):
        chars = list(set([text[i] for text in texts]))
        if len(chars) > 1:
            break
        common.append(chars[0])
    return "".join(common)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--slug', dest='new_slug', metavar='SLUG',
            help='New slug of the merged book (defaults to common part of all slugs).'),
        make_option('-t', '--title', dest='new_title', metavar='TITLE',
            help='New title of the merged book (defaults to common part of all titles).'),
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Less output'),
        make_option('-g', '--guess', action='store_true', dest='guess', default=False,
            help='Try to guess what merges are needed (but do not apply them).'),
        make_option('-d', '--dry-run', action='store_true', dest='dry_run', default=False,
            help='Dry run: do not actually change anything.'),
        make_option('-f', '--force', action='store_true', dest='force', default=False,
            help='On slug conflict, hide the original book to archive.'),
    )
    help = 'Merges multiple books into one.'
    args = '[slug]...'


    def print_guess(self, dry_run=True, force=False):
        from collections import defaultdict
        from pipes import quote
        import re
    
        def read_slug(slug):
            res = []
            res.append((re.compile(ur'__?(przedmowa)$'), -1))
            res.append((re.compile(ur'__?(cz(esc)?|ksiega|rozdzial)__?(?P<n>\d*)$'), None))
            res.append((re.compile(ur'__?(rozdzialy__?)?(?P<n>\d*)-'), None))
        
            for r, default in res:
                m = r.search(slug)
                if m:
                    start = m.start()
                    try:
                        return int(m.group('n')), slug[:start]
                    except IndexError:
                        return default, slug[:start]
            return None, slug
    
        def file_to_title(fname):
            """ Returns a title-like version of a filename. """
            parts = (p.replace('_', ' ').title() for p in fname.split('__'))
            return ' / '.join(parts)
    
        merges = defaultdict(list)
        slugs = []
        for b in Book.objects.all():
            slugs.append(b.slug)
            n, ns = read_slug(b.slug)
            if n is not None:
                merges[ns].append((n, b))
    
        conflicting_slugs = []
        for slug in sorted(merges.keys()):
            merge_list = sorted(merges[slug])
            if len(merge_list) < 2:
                continue
    
            merge_slugs = [b.slug for i, b in merge_list]
            if slug in slugs and slug not in merge_slugs:
                conflicting_slugs.append(slug)
    
            title = file_to_title(slug)
            print "./manage.py merge_books %s%s--title=%s --slug=%s \\\n    %s\n" % (
                '--dry-run ' if dry_run else '',
                '--force ' if force else '',
                quote(title), slug,
                " \\\n    ".join(merge_slugs)
                )
    
        if conflicting_slugs:
            if force:
                print self.style.NOTICE('# These books will be archived:')
            else:
                print self.style.ERROR('# ERROR: Conflicting slugs:')
            for slug in conflicting_slugs:
                print '#', slug


    def handle(self, *slugs, **options):

        self.style = color_style()

        force = options.get('force')
        guess = options.get('guess')
        dry_run = options.get('dry_run')
        new_slug = options.get('new_slug').decode('utf-8')
        new_title = options.get('new_title').decode('utf-8')
        verbose = options.get('verbose')

        if guess:
            if slugs:
                print "Please specify either slugs, or --guess."
                return
            else:
                self.print_guess(dry_run, force)
                return
        if not slugs:
            print "Please specify some book slugs"
            return

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        books = [Book.objects.get(slug=slug) for slug in slugs]
        common_slug = common_prefix(slugs)
        common_title = common_prefix([b.title for b in books])

        if not new_title:
            new_title = common_title
        elif common_title.startswith(new_title):
            common_title = new_title

        if not new_slug:
            new_slug = common_slug
        elif common_slug.startswith(new_slug):
            common_slug = new_slug

        if slugs[0] != new_slug and Book.objects.filter(slug=new_slug).exists():
            self.style.ERROR('Book already exists, skipping!')


        if dry_run and verbose:
            print self.style.NOTICE('DRY RUN: nothing will be changed.')
            print

        if verbose:
            print "New title:", self.style.NOTICE(new_title)
            print "New slug:", self.style.NOTICE(new_slug)
            print

        for i, book in enumerate(books):
            chunk_titles = []
            chunk_slugs = []

            book_title = book.title[len(common_title):].replace(' / ', ' ').lstrip()
            book_slug = book.slug[len(common_slug):].replace('__', '_').lstrip('-_')
            for j, chunk in enumerate(book):
                if j:
                    new_chunk_title = book_title + '_%d' % j
                    new_chunk_slug = book_slug + '_%d' % j
                else:
                    new_chunk_title, new_chunk_slug = book_title, book_slug

                chunk_titles.append(new_chunk_title)
                chunk_slugs.append(new_chunk_slug)

                if verbose:
                    print "title: %s // %s  -->\n       %s // %s\nslug: %s / %s  -->\n      %s / %s" % (
                        book.title, chunk.title,
                        new_title, new_chunk_title,
                        book.slug, chunk.slug,
                        new_slug, new_chunk_slug)
                    print

            if not dry_run:
                try:
                    conflict = Book.objects.get(slug=new_slug)
                except Book.DoesNotExist:
                    conflict = None
                else:
                    if conflict == books[0]:
                        conflict = None

                if conflict:
                    if force:
                        # FIXME: there still may be a conflict
                        conflict.slug = '.' + conflict.slug
                        conflict.save()
                        print self.style.NOTICE('Book with slug "%s" moved to "%s".' % (new_slug, conflict.slug))
                    else:
                        print self.style.ERROR('ERROR: Book with slug "%s" exists.' % new_slug)
                        return

                if i:
                    books[0].append(books[i], slugs=chunk_slugs, titles=chunk_titles)
                else:
                    book.title = new_title
                    book.slug = new_slug
                    book.save()
                    for j, chunk in enumerate(book):
                        chunk.title = chunk_titles[j]
                        chunk.slug = chunk_slugs[j]
                        chunk.save()


        transaction.commit()
        transaction.leave_transaction_management()

