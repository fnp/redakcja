from nose.tools import *
import wiki.models as models
import shutil
import tempfile


class TestStorageBase:
    def setUp(self):
        self.dirpath = tempfile.mkdtemp(prefix='nosetest_')

    def tearDown(self):
        shutil.rmtree(self.dirpath)


class TestDocumentStorage(TestStorageBase):

    def test_storage_empty(self):
        storage = models.DocumentStorage(self.dirpath)
        eq_(storage.all(), [])
