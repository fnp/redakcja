# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-18 14:43:27$"
__doc__ = "Tests for RAL mercurial backend."

from nose.tools import *

from wlrepo import MercurialLibrary

import os, os.path, tempfile
import shutil

REPO_TEMPLATES = os.path.join( os.path.dirname(__file__), 'data')

def temprepo(name):

    from functools import wraps

    def decorator(func):               
        def decorated(*args, **kwargs):
            clean = False
            try:
                temp = tempfile.mkdtemp("", "testdir_" )
                path = os.path.join(temp, 'repo')
                shutil.copytree(os.path.join(REPO_TEMPLATES, name), path, False)
                kwargs['library'] = MercurialLibrary(path)
                func(*args, **kwargs)
                clean = True
            finally:
                #if not clean and self.response:
                #    print "RESULT", func.__name__, ">>>"
                #    print self.response
                #    print "<<<"
                shutil.rmtree(temp, True)

        decorated = make_decorator(func)(decorated)
        return decorated   
    
    return decorator

@temprepo('clean')
def test_opening(library):
    pass

@temprepo('simple')
def test_read_document(library):
    doc = library.document('sample')
    assert_equal(doc.data('xml'), 'Ala ma kota\n')

@temprepo('simple')
def test_read_UTF8_document(library):
    doc = library.document('sample_pl')
    assert_equal(doc.data('xml'), u'Gżegżółka\n'.encode('utf-8'))

@temprepo('simple')
def test_change_document(library):
    doc = library.document('sample')
    STRING = u'Gąski lubią pływać!\n'.encode('utf-8')
    
    def write_action(library, resolve):
        f = library._fileopen(resolve('xml'), 'r+')        
        assert_equal(f.read(), 'Ala ma kota\n')
        f.seek(0)
        f.write(STRING)
        f.flush()
        f.seek(0)
        assert_equal(f.read(), STRING)

    def commit_info(document):
        return ("Document rewrite", "library")
    
    ndoc = doc.invoke_and_commit(write_action, commit_info)
    assert_equal(ndoc.data('xml'), STRING)
    

@temprepo('simple')
def test_create_document(library):
    assert_equal(sorted(library.documents()), sorted(['sample', 'sample_pl']))

    doc = library.document_create("creation")
    doc.quickwrite("xml", "<ala />", "Quick write", user="library")
    
    assert_equal(sorted(library.documents()), sorted(['sample', 'sample_pl', 'creation']))
        
#
#@temprepo('branched')
#def test_switch_branch(library):
#    tester_cab = library.cabinet("valid_file", "tester", create=False)
#    assert_equal( list(tester_cab.parts()), ['valid_file'])
#
#@raises(wlrepo.CabinetNotFound)
#@temprepo('branched')
#def test_branch_not_found(library):
#    tester_cab = library.cabinet("ugh", "tester", create=False)
#
#@temprepo('branched')
#def test_no_branches(library):
#    n4 = library.shelf(4)
#    n3 = library.shelf(3)
#    n2 = library.shelf(2)
#    n1 = library.shelf(1)
#    n0 = library.shelf(0)
#
#    assert_true( n3.parentof(n4) )
#    assert_false( n4.parentof(n3) )
#    assert_true( n0.parentof(n1) )
#    assert_false( n1.parentof(n0) )
#    assert_false( n0.parentof(n4) )
#
## def test_ancestor_of_simple(self):
#    assert_true( n3.ancestorof(n4) )
#    assert_true( n2.ancestorof(n4) )
#    assert_true( n1.ancestorof(n4) )
#    assert_true( n0.ancestorof(n4) )
#
#    assert_true( n2.ancestorof(n3) )
#    assert_true( n1.ancestorof(n3) )
#    assert_true( n0.ancestorof(n3) )
#
#    assert_false( n4.ancestorof(n4) )
#    assert_false( n4.ancestorof(n3) )
#    assert_false( n3.ancestorof(n2) )
#    assert_false( n3.ancestorof(n1) )
#    assert_false( n3.ancestorof(n0) )
#
## def test_common_ancestor_simple(self):
#    assert_true( n3.has_common_ancestor(n4) )
#    assert_true( n3.has_common_ancestor(n3) )
#    assert_true( n3.has_common_ancestor(n3) )
#
#
#@temprepo('branched2')
#def test_once_branched(library):
#    n7 = library.shelf(7)
#    n6 = library.shelf(6)
#    n5 = library.shelf(5)
#    n4 = library.shelf(4)
#    n3 = library.shelf(3)
#    n2 = library.shelf(2)
#
#    assert_true( n2.parentof(n3) )
#    assert_false( n3.parentof(n2) )
#
#    assert_true( n2.parentof(n5) )
#    assert_false( n5.parentof(n2) )
#
#    assert_false( n2.parentof(n4) )
#    assert_false( n2.parentof(n6) )
#    assert_false( n3.parentof(n5) )
#    assert_false( n5.parentof(n3) )
#
## def test_ancestorof_branched(self):
#    assert_true( n2.ancestorof(n7) )
#    assert_false( n7.ancestorof(n2) )
#    assert_true( n2.ancestorof(n6) )
#    assert_false( n6.ancestorof(n2) )
#    assert_true( n2.ancestorof(n5) )
#    assert_false( n5.ancestorof(n2) )
#
#    assert_false( n3.ancestorof(n5) )
#    assert_false( n5.ancestorof(n3) )
#    assert_false( n4.ancestorof(n5) )
#    assert_false( n5.ancestorof(n4) )
#    assert_false( n3.ancestorof(n7) )
#    assert_false( n7.ancestorof(n3) )
#    assert_false( n4.ancestorof(n6) )
#    assert_false( n6.ancestorof(n4) )
#
## def test_common_ancestor_branched(self):
#    assert_true( n2.has_common_ancestor(n4) )
#    assert_true( n2.has_common_ancestor(n7) )
#    assert_true( n2.has_common_ancestor(n6) )
#
#    # cause it's not in the right branch
#    assert_false( n5.has_common_ancestor(n3) )
#    assert_false( n7.has_common_ancestor(n4) )
#
#@temprepo('merged')
#def test_after_merge(library):
#    n8 = library.shelf(8)
#    n7 = library.shelf(7)
#    n6 = library.shelf(6)
#
#    assert_true( n7.parentof(n8) )
#    assert_false( n8.parentof(n7) )
#
#    assert_true( n7.ancestorof(n8) )
#    assert_true( n6.ancestorof(n8) )
#
#
#    assert_true( n7.has_common_ancestor(n8) )
#    # cause it's not in the right branch
#    assert_false( n8.has_common_ancestor(n7) )
#
#@temprepo('merged_with_local_commit')
#def test_after_merge_and_local_commit(library):
#    n9 = library.shelf(9)
#    n8 = library.shelf(8)
#    n7 = library.shelf(7)
#    n6 = library.shelf(6)
#
#    assert_true( n7.parentof(n8) )
#    assert_false( n8.parentof(n7) )
#
#    assert_true( n9.has_common_ancestor(n8) )
#    # cause it's not in the right branch
#    assert_false( n8.has_common_ancestor(n9) )
#
#
#@temprepo('branched2')
#def test_merge_personal_to_default(library):
#    main = library.shelf(2)
#    print main
#
#    local = library.shelf(7)
#    print local
#
#    document = library.document("ala", "admin")
#    shared = document.shared()
#    assert_true( shared is None )
#    document.share("Here is my copy!")
#
#    assert_equal( document.shelf(), local) # local didn't change
#
#    shared = document.shared()
#    assert_true( shared is not None )
#
#    print library.shelf()
#
#    new_main = shared.shelf()
#    assert_not_equal( new_main, main) # main has new revision
#
#    # check for parents
#    assert_true( main.parentof(new_main) )
#    assert_true( local.parentof(new_main) )
#
#@temprepo('clean')
#def test_create_branch(library):
#    tester_cab = library.cabinet("anotherone", "tester", create=True)
#    assert_equal( list(tester_cab.parts()), ['anotherone'])

