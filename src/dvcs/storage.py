from zlib import compress, decompress

from django.core.files.base import ContentFile, File
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class GzipFileSystemStorage(FileSystemStorage):
    def _open(self, name, mode='rb'):
        """TODO: This is good for reading; what about writing?"""
        f = open(self.path(name), 'rb')
        text = f.read()
        f.close()
        return ContentFile(decompress(text))

    def _save(self, name, content):
        content = ContentFile(compress(content.read()))

        return super(GzipFileSystemStorage, self)._save(name, content)
