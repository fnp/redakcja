# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
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
