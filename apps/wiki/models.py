import re
import vstorage
from vstorage import DocumentNotFound
from wiki import settings

class DocumentStorage(object):
    def __init__(self, path):
        self.vstorage = vstorage.VersionedStorage(path)

    def get(self, name, revision = None):
        if revision is None:
            text = self.vstorage.page_text(name)
        else:
            text = self.vstorage.revision_text(name, revision)
        return Document(self, name = name, text = text)

    def put(self, document, author, comment, parent):
        self.vstorage.save_text(document.name, document.text, author, comment, parent)

    def delete(self, name, author, comment):
        self.vstorage.delete_page(name, author, comment)

    def all(self):
        return list(self.vstorage.all_pages())
    
    def history(self, title):
        return list(self.vstorage.page_history(title))

    def _info(self, name):
        return self.vstorage.page_meta(name)


class Document(object):
    META_REGEX = re.compile(r'\s*<!--\s(.*?)-->', re.DOTALL | re.MULTILINE)

    def __init__(self, storage, **kwargs):
        self.storage = storage
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def revision(self):
        try:
            return self.storage._info(self.name)[0]
        except DocumentNotFound:
            return - 1

    @property
    def plain_text(self):
        return re.sub(self.META_REGEX, '', self.text, 1)

    def meta(self):
        result = {}

        m = re.match(self.META_REGEX, self.text)
        if m:
            for line in m.group(1).split('\n'):
                try:
                    k, v = line.split(':', 1)
                    result[k.strip()] = v.strip()
                except ValueError:
                    continue

        return result

# Every time somebody says "let's have a global variable", God kills a kitten.
storage = DocumentStorage(settings.REPOSITORY_PATH)
