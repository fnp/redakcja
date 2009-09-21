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
   
    def testOpening(self):
        library = MercurialLibrary(self.path + '/cleanrepo')

    def testMainCabinet(self):
        library = MercurialLibrary(self.path + '/cleanrepo')

        mcab = library.main_cabinet
        assert_equal(mcab.maindoc_name(), '')

        # @type mcab MercurialCabinet
        doclist = mcab.documents()
        assert_equal( list(doclist), ['valid_file'])


    def testReadDocument(self):
        library = MercurialLibrary(self.path + '/testrepoI')
        doc = library.main_cabinet.retrieve('valid_file')
        
        assert_equal(doc.read().strip(), 'Ala ma kota')

    def testReadUTF8Document(self):
        library = MercurialLibrary(self.path + '/testrepoI')
        doc = library.main_cabinet.retrieve('polish_file')

        assert_equal(doc.read().strip(), u'Gąska!'.encode('utf-8'))

    def testWriteDocument(self):
        library = MercurialLibrary(self.path + '/testrepoI')
        doc = library.main_cabinet.retrieve('valid_file')

        assert_equal(doc.read().strip(), 'Ala ma kota')
        
        STRING = u'Gąski lubią pływać!\n'.encode('utf-8')
        doc.write(STRING)       
        
        assert_equal(doc.read(), STRING)

    def testCreateDocument(self):
        repopath = os.path.join(self.path, 'testrepoI')

        library = MercurialLibrary(repopath)
        doc = library.main_cabinet.create("another_file")
        doc.write("Some text")
        assert_equal( doc.read(), "Some text")
        assert_true( os.path.isfile( os.path.join(repopath, "pub_another_file.xml")) )
        
    def testSwitchBranch(self):
        library = MercurialLibrary(self.path + '/testrepoII')

        tester_cab = library.cabinet("valid_file", "tester", create=False)
        assert_equal( list(tester_cab.documents()), ['valid_file'])

    @raises(wlrepo.CabinetNotFound)
    def testNoBranch(self):
        library = MercurialLibrary(self.path + '/testrepoII')
        tester_cab = library.cabinet("ugh", "tester", create=False)


    def testCreateBranch(self):
        repopath = os.path.join(self.path, 'testrepoII')
        library = MercurialLibrary(repopath)

        tester_cab = library.cabinet("anotherone", "tester", create=True)       
        assert_equal( list(tester_cab.documents()), ['anotherone'])

        

        