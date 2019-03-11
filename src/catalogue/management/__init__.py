# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import defaultdict
from django.db import transaction
from lxml import etree


class XmlUpdater(object):
    """A base class for massive XML updates.

    In a subclass, override `fix_tree` and/or use `fixes_field` decorator.
    Attributes:
    * commit_desc: commits description
    * retain_publishable: set publishable if head is (default: True)
    * only_first_chunk: process only first chunks of books (default: False)
    """
    commit_desc = "auto-update"
    retain_publishable = True
    only_first_chunk = False

    _element_fixers = defaultdict(list)

    def __init__(self):
        self.counters = defaultdict(lambda: 0)

    @classmethod
    def fixes_elements(cls, xpath):
        """Decorator, registering a function as a fixer for given field type.

        Any decorated function will be called like
            f(element, change=..., verbose=...)
        providing changeset as context.

        :param xpath: element lookup, e.g. ".//{namespace-uri}tag-name"
        :returns: True if anything changed
        """
        def wrapper(fixer):
            cls._element_fixers[xpath].append(fixer)
            return fixer
        return wrapper

    def fix_tree(self, tree, verbose):
        """Override to provide general tree-fixing mechanism.

        :param tree: the parsed XML tree
        :param verbose: verbosity level
        :returns: True if anythig changed
        """
        return False

    def fix_chunk(self, chunk, user, verbose=0, dry_run=False):
        """Runs the update for a single chunk."""
        if verbose >= 2:
            print(chunk.get_absolute_url())
        old_head = chunk.head
        src = old_head.materialize()
        try:
            tree = etree.fromstring(src)
        except:
            if verbose:
                print("%s: invalid XML" % chunk.get_absolute_url())
            self.counters['Bad XML'] += 1
            return

        dirty = False
        # Call the general fixing function.
        if self.fix_tree(tree, verbose=verbose):
            dirty = True
        # Call the registered fixers.
        for xpath, fixers in self._element_fixers.items():
            for elem in tree.findall(xpath):
                for fixer in fixers:
                    if fixer(elem, change=old_head, verbose=verbose):
                        dirty = True

        if not dirty:
            self.counters['Clean'] += 1
            return

        if not dry_run:
            new_head = chunk.commit(
                etree.tostring(tree, encoding='unicode'),
                author=user,
                description=self.commit_desc
            )
            if self.retain_publishable:
                if old_head.publishable:
                    new_head.set_publishable(True)
        if verbose >= 2:
            print("done")
        self.counters['Updated chunks'] += 1

    def run(self, user, verbose=0, dry_run=False, books=None):
        """Runs the actual update."""
        if books is None:
            from catalogue.models import Book
            books = Book.objects.all()

        # Start transaction management.
        with transaction.atomic():
            for book in books:
                self.counters['All books'] += 1
                chunks = book.chunk_set.all()
                if self.only_first_chunk:
                    chunks = chunks[:1]
                for chunk in chunks:
                    self.counters['All chunks'] += 1
                    self.fix_chunk(chunk, user, verbose, dry_run)

    def print_results(self):
        """Prints the counters."""
        for item in sorted(self.counters.items()):
            print("%s: %d" % item)
