import vstorage
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
    
    def put(self, name, document, author, comment, parent):
        self.vstorage.save_text(document.name, document.text, author, comment, parent)

    def delete(name, author, comment):
        self.vstorage.delete_page(name, author, comment)


class Document(object):
    def __init__(self, storage, **kwargs):
        self.storage = storage
        for attr, value in kwargs:
            setattr(self, attr, value)


storage = DocumentStorage(settings.REPOSITORY_PATH)

