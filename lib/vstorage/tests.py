#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

import os
import tempfile
from nose.tools import *
from nose.core import runmodule

import vstorage

def clear_directory(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    try:
        os.removedirs(top)
    except OSError:
        pass


class TestVersionedStorage(object):
    def setUp(self):
        self.repo_path = tempfile.mkdtemp()
        self.repo = vstorage.VersionedStorage(self.repo_path)

    def tearDown(self):
        clear_directory(self.repo_path)

    def test_save_text(self):
        text = u"test text"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"

        self.repo.save_text(
            title=title,
            text=text,
            author=author,
            comment=comment,
            parent=None,
        )

        saved_text, rev = self.repo.page_text(title)
        assert_equal(saved_text, text)
        assert_equal(rev, 0)

    def test_save_text_noparent(self):
        text = u"test text"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"

        self.repo.save_text(title=title,
                    text=text, author=author,
                    comment=comment, parent=None)

        saved_text, rev = self.repo.page_text(title)
        assert_equal(saved_text, text)
        assert_equal(rev, 0)

    def test_save_merge_no_conflict(self):
        text = u"test\ntext"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"
        self.repo.save_text(title=title,
                    text=text, author=author,
                    comment=comment, parent=None)
        self.repo.save_text(title=title,
                    text=text, author=author,
                    comment=comment, parent=None)

        saved_text, rev = self.repo.page_text(title)
        assert_equal(saved_text, text)
        assert_equal(rev, 0)

    def test_save_merge_line_conflict(self):
        text = u"test\ntest\n"
        text1 = u"test\ntext\n"
        text2 = u"text\ntest\n"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"

        self.repo.save_text(title=title,
                    text=text, author=author,
                    comment=comment, parent=None)

        saved_text, rev = self.repo.page_text(title)
        assert_equal(saved_text, text)
        assert_equal(rev, 0)

        self.repo.save_text(title=title,
                    text=text1, author=author,
                    comment=comment, parent=0)

        saved_text, rev = self.repo.page_text(title)
        assert_equal(saved_text, text1)
        assert_equal(rev, 1)

        self.repo.save_text(title=title,
                    text=text2, author=author,
                    comment=comment, parent=0)

        saved_text, rev = self.repo.page_text(title)
        # Other conflict markers placement can also be correct
        assert_equal(saved_text, u'''\
text
test
<<<<<<< local
=======
text
>>>>>>> other
''')

    def test_delete(self):
        text = u"text test"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"
        self.repo.save_text(title=title,
                    text=text, author=author,
                    comment=comment, parent=None)

        assert title in self.repo

        self.repo.delete_page(title, author, comment)

        assert title not in self.repo

    @raises(vstorage.DocumentNotFound)
    def test_document_not_found(self):
        self.repo.page_text(u'unknown entity')

    def test_open_existing_repository(self):
        self.repo.save_text(title=u'Python!', text=u'ham and spam')
        current_repo_revision = self.repo.repo_revision()
        same_repo = vstorage.VersionedStorage(self.repo_path)
        assert_equal(same_repo.repo_revision(), current_repo_revision)

    def test_history(self):
        COMMITS = [
            {"author": "bunny", "text":"1", "comment": "Oh yeah!"},
            {"author": "frank", "text":"2", "comment": "Second is the best!"},
            {"text":"3", "comment": "Third"},
            {"author": "welma", "text":"4", "comment": "Fourth"},
        ]

        for commit in COMMITS:
            self.repo.save_text(title=u"Sample", **commit)

        for n, entry in enumerate(reversed(list(self.repo.page_history(u"Sample")))):
            assert_equal(entry["version"], n)
            assert_equal(entry["author"], COMMITS[n].get("author", "anonymous"))
            assert_equal(entry["description"], COMMITS[n]["comment"])
            assert_equal(entry["tag"], [])


class TestVSTags(object):

    TITLE_1 = "Sample"

    COMMITS = [
        {"author": "bunny", "text":"1", "comment": "Oh yeah!"},
        {"author": "frank", "text":"2", "comment": "Second is the best!"},
        {"text":"3", "comment": "Third"},
        {"author": "welma", "text":"4", "comment": "Fourth"},
    ]

    def setUp(self):
        self.repo_path = tempfile.mkdtemp()
        self.repo = vstorage.VersionedStorage(self.repo_path)

        # generate some history
        for commit in self.COMMITS:
            self.repo.save_text(title=u"Sample", **commit)

        # verify
        for n, entry in enumerate(reversed(list(self.repo.page_history(self.TITLE_1)))):
            assert_equal(entry["tag"], [])

    def tearDown(self):
        clear_directory(self.repo_path)

    def test_add_tag(self):
        TAG_USER = "mike_the_tagger"
        TAG_NAME = "production"
        TAG_VERSION = 2

        # Add tag
        self.repo.add_page_tag(self.TITLE_1, TAG_VERSION, TAG_NAME, TAG_USER)

        # check history again
        history = list(self.repo.page_history(self.TITLE_1))
        for entry in reversed(history):
            if entry["version"] == TAG_VERSION:
                assert_equal(entry["tag"], [TAG_NAME])
            else:
                assert_equal(entry["tag"], [])

    def test_add_many_tags(self):
        TAG_USER = "mike_the_tagger"
        tags = [
            (2, "production", "mike"),
            (2, "finished", "jeremy"),
            (0, "original", "jeremy"),
        ]

        for rev, name, user in tags:
            self.repo.add_page_tag(self.TITLE_1, rev, name, user)

        # check history again
        history = list(self.repo.page_history(self.TITLE_1))
        for entry in reversed(history):
            expected = [tag[1] for tag in tags if tag[0] == entry["version"]]
            assert_equal(set(entry["tag"]), set(expected))
