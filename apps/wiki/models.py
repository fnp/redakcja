import vstorage
from vstorage import DocumentNotFound
from wiki import settings


class DocumentStorage(object):
    def __init__(self, path):
        self.vstorage = vstorage.VersionedStorage(path)
    
    def get(self, name, revision=None):
        if revision is None:
            text = self.vstorage.page_text(name)
        else:
            text = self.vstorage.revision_text(name, revision)
        return Document(self, name=name, text=text)
    
    def put(self, document, author, comment, parent):
        self.vstorage.save_text(document.name, document.text, author, comment, parent)

    def delete(self, name, author, comment):
        self.vstorage.delete_page(name, author, comment)

    def all(self):
        return list(self.vstorage.all_pages())

    def _info(self, name):
        return self.vstorage.page_meta(name)


class Document(object):
    def __init__(self, storage, **kwargs):
        self.storage = storage
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
            
    def revision(self):
        try:
            return self.storage._info(self.name)[0]
        except DocumentNotFound:
            return -1


storage = DocumentStorage(settings.REPOSITORY_PATH)

