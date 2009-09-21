"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from django.utils import simplejson as json

from django.contrib.auth.models import User

import settings
from os.path import join, dirname
from StringIO import StringIO
import shutil
import tempfile

REPO_TEMPLATES = join(dirname(__file__), 'data')

def temprepo(name):
    def decorator(func):   
        def decorated(self, *args, **kwargs):
            clean = False
            try:
                temp = tempfile.mkdtemp("", "testdir_" )
                shutil.copytree(join(REPO_TEMPLATES, name), join(temp, 'repo'), False)
                settings.REPOSITORY_PATH = join(temp, 'repo')
                func(self, *args, **kwargs)
                clean = True
            finally:
                if not clean and self.response:
                    print "RESULT", func.__name__, ">>>"
                    print self.response
                    print "<<<"

                shutil.rmtree(temp, True)
                settings.REPOSITORY_PATH = ''
            
        return decorated
    return decorator   
    

class SimpleTest(TestCase):

    def setUp(self):
        self.response = None
        u = User.objects.create_user('admin', 'test@localhost', 'admin')
        u.save()        

    @temprepo('empty')
    def test_documents_get_anonymous(self):
        self.response = self.client.get( reverse("document_list_view") )
        self.assert_json_response({
            u'latest_rev': u'e56b2a7e06a97d7c3697fc4295974e0f20a66190',
            u'documents': [],
            u'cabinet': u'default',
        }, exclude=['latest_shared_rev'])

    @temprepo('empty')
    def test_documents_get_with_login(self):
        self.assertTrue(self.client.login(username='admin', password='admin'))
        
        self.response = self.client.get( reverse("document_list_view") )
        self.assert_json_response({            
            u'latest_rev': u'e56b2a7e06a97d7c3697fc4295974e0f20a66190',
            u'documents': [],
            u'cabinet': u'default',
        })    

    @temprepo('empty')
    def test_documents_post(self):
        self.assertTrue(self.client.login(username='admin', password='admin'))

        infile = tempfile.NamedTemporaryFile("w+")
        infile.write('0123456789')
        infile.flush()
        infile.seek(0)
        
        self.response = self.client.post( reverse("document_list_view"),               
        data = {
             'bookname': 'testbook',
             'ocr': infile,
             'generate_dc': False,
        })

        infile.close()
        
        result = self.assert_json_response({
            'url': reverse('document_view', args=['testbook']),
            'name': 'testbook',
            'size': 10,
            # can't test revision number, 'cause it's random
        },)

    @temprepo('empty')        
    def test_document_creation(self):
        self.assertTrue(self.client.login(username='admin', password='admin'))

        infile = tempfile.NamedTemporaryFile("w+")
        infile.write('012340123456789')
        infile.flush()
        infile.seek(0)

        self.response = self.client.post( reverse("document_list_view"),
        data = {
             'bookname': 'testbook',
             'ocr': infile,
             'generate_dc': False,
        })
        
        r = self.assert_json_response({
            'url': reverse('document_view', args=['testbook']),
            'name': 'testbook',
            'size': 15,
            # can't test revision number, 'cause it's random
        })

        created_rev = r['revision']

        self.response = self.client.get( \
            reverse("document_view", args=["testbook"])+'?autocabinet=true' )

        result = self.assert_json_response({
            u'latest_shared_rev': created_rev,
            u'size': 15,
        })


    @temprepo('testone')
    def test_document_meta_get_with_login(self):
        self.assertTrue(self.client.login(username='admin', password='admin'))

        self.response = self.client.get( reverse("document_list_view") )
        self.assert_json_response({
            u'latest_rev': u'f94a263812dbe46a3a13d5209bb119988d0078d5',
            u'documents': [{u'url': u'/api/documents/testfile', u'name': u'testfile'}],
            u'cabinet': u'default',
        })

        self.response = self.client.get( \
            reverse("document_view", args=['testfile'])+'?autocabinet=true' )

        self.assert_json_response({
            u'latest_shared_rev': u'f94a263812dbe46a3a13d5209bb119988d0078d5',
            u'text_url': reverse("doctext_view", args=[u'testfile']),
            u'dc_url': reverse("docdc_view", args=[u'testfile']),
            u'parts_url': reverse("docparts_view", args=[u'testfile']),
            u'name': u'testfile',
            u'size': 20,
        })
        
        
    @temprepo('test2')
    def test_document_text_with_login(self):
        self.assertTrue(self.client.login(username='admin', password='admin'))
        
        self.response = self.client.get( \
            reverse("doctext_view", args=['testfile']) )

        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, "Test file contents.\n")


    @temprepo('test2')
    def test_document_text_update(self):
        self.assertTrue(self.client.login(username='admin', password='admin'))
        TEXT = u"Ala ma kota i psa"
        
        self.response = self.client.put( \
            reverse("doctext_view", args=['testfile']), {'contents': TEXT })
        self.assertEqual(self.response.status_code, 200)

        self.response = self.client.get( \
            reverse("doctext_view", args=['testfile']) )
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, TEXT)

    def assert_json_response(self, must_have={}, exclude=[]):
        self.assertEqual(self.response.status_code, 200)
        result = json.loads(self.response.content)

        for (k,v) in must_have.items():
            self.assertTrue(result.has_key(k), "Required field '%s' missing in response." % k)
            self.assertEqual(result[k], v)

        if exclude is True:
            for (k,v) in result.items():
                self.assertTrue(must_have.has_key(k))
                self.assertEqual(must_have[k], v)

        for key in exclude:
            self.assertFalse(result.has_key(key))
            
        return result   
              