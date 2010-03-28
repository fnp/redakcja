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
        
        self.repo.save_text(title = title, 
                    text = text, author = author, 
                    comment = comment, parent=-1)
        
        saved = self.repo.open_page(title).read()
        assert saved == text

    def test_save_text_noparent(self):
        text = u"test text"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"
        
        self.repo.save_text(title = title, 
                    text = text, author = author, 
                    comment = comment, parent=None)
        
        saved = self.repo.open_page(title).read()
        assert saved == text

    def test_save_merge_no_conflict(self):
        text = u"test\ntext"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"
        self.repo.save_text(title = title, 
                    text = text, author = author, 
                    comment = comment, parent=-1)
        self.repo.save_text(title = title, 
                    text = text, author = author, 
                    comment = comment, parent=-1)
        saved = self.repo.open_page(title).read()
        assert saved == text
    
    def test_save_merge_line_conflict(self):
        text = u"test\ntest\n"
        text1 = u"test\ntext\n"
        text2 = u"text\ntest\n"
        title = u"test title"
        author = u"test author"
        comment = u"test comment"
        
        self.repo.save_text(title = title, 
                    text = text, author = author, 
                    comment = comment, parent=-1)
        
        self.repo.save_text(title = title, 
                    text = text1, author = author, 
                    comment = comment, parent=0)
        
        self.repo.save_text(title = title, 
                    text = text2, author = author, 
                    comment = comment, parent=0)
        
        saved = self.repo.open_page(title).read()
        
        # Other conflict markers placement can also be correct
        assert_equal(saved, u'''\
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
        self.repo.save_text(title = title, 
                    text = text, author = author, 
                    comment = comment, parent=-1)
        
        assert title in self.repo
        
        self.repo.delete_page(title, author, comment)
        
        assert title not in self.repo

    @raises(vstorage.DocumentNotFound)
    def test_document_not_found(self):
        self.repo.open_page(u'unknown entity')

    def test_open_existing_repository(self):
        self.repo.save_text(title = u'Python!', text = u'ham and spam')
        current_repo_revision = self.repo.repo_revision()
        same_repo = vstorage.VersionedStorage(self.repo_path)
        assert same_repo.repo_revision() == current_repo_revision


if __name__ == '__main__':
    runmodule()