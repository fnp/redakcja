import wiki.models as models
import shutil
import tempfile


class TestStorageBase:
    def setUp(self):
        self.dirpath = tempfile.mkdtemp(prefix='redakcja_test_')

    def tearDown(self):
        shutil.rmtree(self.dirpath)


class TestDocumentStorage(TestStorageBase):

    def test_storage_empty(self):
        storage = models.DocumentStorage(self.dirpath)
        self.assertEqual(storage.all(), [])
