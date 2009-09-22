# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-18 14:43:27$"
__doc__ = "Tests for RAL mercurial backend."

from nose.tools import *

import wlrepo
from wlrepo import MercurialLibrary
from wlrepo.backend_mercurial import *

import os, os.path, tempfile
import shutil

REPO_TEMPLATES = os.path.join( os.path.dirname(__file__), 'data/repos')
ROOT_PATH = None

class testBasicLibrary(object):

    def setUp(self):
        self.path = tempfile.mkdtemp("", "testdir_" )
        print self.path
        for subdir in os.listdir(REPO_TEMPLATES):
            shutil.copytree(REPO_TEMPLATES + '/' + subdir, self.path + '/' + subdir, False)

    def tearDown(self):        
        if self.path is not None:
            shutil.rmtree(self.path, True)
        pass
   
    def test_opening(self):
        library = MercurialLibrary(self.path + '/cleanrepo')

    def test_main_cabinett(self):
        library = MercurialLibrary(self.path + '/cleanrepo')

        mcab = library.main_cabinet
        assert_equal(mcab.maindoc_name, '')

        # @type mcab MercurialCabinet
        doclist = mcab.documents()
        assert_equal( list(doclist), ['valid_file'])


    def test_read_document(self):
        library = MercurialLibrary(self.path + '/testrepoI')
        doc = library.main_cabinet.retrieve('valid_file')
        
        assert_equal(doc.read().strip(), 'Ala ma kota')

    def test_read_UTF8_document(self):
        library = MercurialLibrary(self.path + '/testrepoI')
        doc = library.main_cabinet.retrieve('polish_file')

        assert_equal(doc.read().strip(), u'Gąska!'.encode('utf-8'))

    def test_write_document(self):
        library = MercurialLibrary(self.path + '/testrepoI')
        doc = library.main_cabinet.retrieve('valid_file')

        assert_equal(doc.read().strip(), 'Ala ma kota')
        
        STRING = u'Gąski lubią pływać!\n'.encode('utf-8')
        doc.write(STRING)       
        
        assert_equal(doc.read(), STRING)

    def test_create_document(self):
        repopath = os.path.join(self.path, 'testrepoI')

        library = MercurialLibrary(repopath)
        doc = library.main_cabinet.create("another_file", "Some text")
        assert_equal( doc.read(), "Some text")
        assert_true( os.path.isfile( os.path.join(repopath, "pub_another_file.xml")) )
        
    def test_switch_branch(self):
        library = MercurialLibrary(self.path + '/testrepoII')

        tester_cab = library.cabinet("valid_file", "tester", create=False)
        assert_equal( list(tester_cab.documents()), ['valid_file'])

    @raises(wlrepo.CabinetNotFound)
    def test_branch_not_found(self):
        library = MercurialLibrary(self.path + '/testrepoII')
        tester_cab = library.cabinet("ugh", "tester", create=False)

    def test_no_branches(self):
        library = MercurialLibrary(self.path + '/testrepoII')
        n4 = library.shelf(4)
        n3 = library.shelf(3)
        n2 = library.shelf(2)
        n1 = library.shelf(1)
        n0 = library.shelf(0)

        assert_true( n3.parentof(n4) )
        assert_false( n4.parentof(n3) )
        assert_true( n0.parentof(n1) )
        assert_false( n1.parentof(n0) )
        assert_false( n0.parentof(n4) )

    # def test_ancestor_of_simple(self):
        assert_true( n3.ancestorof(n4) )
        assert_true( n2.ancestorof(n4) )
        assert_true( n1.ancestorof(n4) )
        assert_true( n0.ancestorof(n4) )

        assert_true( n2.ancestorof(n3) )
        assert_true( n1.ancestorof(n3) )
        assert_true( n0.ancestorof(n3) )

        assert_false( n4.ancestorof(n4) )
        assert_false( n4.ancestorof(n3) )
        assert_false( n3.ancestorof(n2) )
        assert_false( n3.ancestorof(n1) )
        assert_false( n3.ancestorof(n0) )

    # def test_common_ancestor_simple(self):
        assert_true( n3.has_common_ancestor(n4) )
        assert_true( n3.has_common_ancestor(n3) )
        assert_true( n3.has_common_ancestor(n3) )


    def test_once_branched(self):
        library = MercurialLibrary(self.path + '/test3')

        n7 = library.shelf(7)
        n6 = library.shelf(6)
        n5 = library.shelf(5)
        n4 = library.shelf(4)
        n3 = library.shelf(3)
        n2 = library.shelf(2)

        assert_true( n2.parentof(n3) )
        assert_false( n3.parentof(n2) )

        assert_true( n2.parentof(n5) )
        assert_false( n5.parentof(n2) )

        assert_false( n2.parentof(n4) )
        assert_false( n2.parentof(n6) )
        assert_false( n3.parentof(n5) )
        assert_false( n5.parentof(n3) )

    # def test_ancestorof_branched(self):
        assert_true( n2.ancestorof(n7) )
        assert_false( n7.ancestorof(n2) )
        assert_true( n2.ancestorof(n6) )
        assert_false( n6.ancestorof(n2) )
        assert_true( n2.ancestorof(n5) )
        assert_false( n5.ancestorof(n2) )

        assert_false( n3.ancestorof(n5) )
        assert_false( n5.ancestorof(n3) )
        assert_false( n4.ancestorof(n5) )
        assert_false( n5.ancestorof(n4) )
        assert_false( n3.ancestorof(n7) )
        assert_false( n7.ancestorof(n3) )
        assert_false( n4.ancestorof(n6) )
        assert_false( n6.ancestorof(n4) )

    # def test_common_ancestor_branched(self):
        assert_true( n2.has_common_ancestor(n4) )
        assert_true( n2.has_common_ancestor(n7) )
        assert_true( n2.has_common_ancestor(n6) )

        # cause it's not in the right branch
        assert_false( n5.has_common_ancestor(n3) )
        assert_false( n7.has_common_ancestor(n4) )

    def test_after_merge(self):
        library = MercurialLibrary(self.path + '/test4')
        n8 = library.shelf(8)
        n7 = library.shelf(7)
        n6 = library.shelf(6)

        assert_true( n7.parentof(n8) )
        assert_false( n8.parentof(n7) )
        
        assert_true( n7.ancestorof(n8) )
        assert_true( n6.ancestorof(n8) )
        

        assert_true( n7.has_common_ancestor(n8) )
        # cause it's not in the right branch
        assert_false( n8.has_common_ancestor(n7) )


    def test_after_merge_and_local_commit(self):
        library = MercurialLibrary(self.path + '/test5b')
        n9 = library.shelf(9)
        n8 = library.shelf(8)
        n7 = library.shelf(7)
        n6 = library.shelf(6)

        assert_true( n7.parentof(n8) )
        assert_false( n8.parentof(n7) )

        assert_true( n9.has_common_ancestor(n8) )
        # cause it's not in the right branch
        assert_false( n8.has_common_ancestor(n9) )


    def test_merge_personal_to_default(self):
        library = MercurialLibrary(self.path + '/test3')

        main = library.shelf(2)
        local = library.shelf(7)

        document = library.document("ala", "admin")
        shared = document.shared()
        print document, shared

        document.share("Here is my copy!")

        assert_equal( document.shelf(), local) # local didn't change

        
        new_main = shared.shelf()
        assert_not_equal( new_main, main) # main has new revision

        # check for parents
        assert_true( main.parentof(new_main) )
        assert_true( local.parentof(new_main) )
        
        

    def testCreateBranch(self):
        repopath = os.path.join(self.path, 'testrepoII')
        library = MercurialLibrary(repopath)

        tester_cab = library.cabinet("anotherone", "tester", create=True)       
        assert_equal( list(tester_cab.documents()), ['anotherone'])

        


