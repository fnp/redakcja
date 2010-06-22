class XMLNamespace(object):
    '''A handy structure to represent names in an XML namespace.'''

    def __init__(self, uri):
        self.uri = uri

    def __call__(self, tag):
        return '{%s}%s' % (self.uri, tag)

    def __contains__(self, tag):
        return tag.startswith('{' + self.uri + '}')

    def __repr__(self):
        return 'XMLNamespace(%r)' % self.uri

    def __str__(self):
        return '%s' % self.uri

    def strip(self, qtag):
        if qtag not in self:
            raise ValueError("Tag %s not in namespace %s" % (qtag, self.uri))
        return qtag[len(self.uri) + 2:]

    @classmethod
    def split_tag(cls, tag):
        if '{' != tag[0]:
            raise ValueError
        end = tag.find('}')
        if end < 0:
            raise ValueError
        return cls(tag[1:end]), tag[end + 1:]

    @classmethod
    def tagname(cls, tag):
        return cls.split_tag(tag)[1]


class EmptyNamespace(XMLNamespace):
    def __init__(self):
        super(EmptyNamespace, self).__init__('')

    def __call__(self, tag):
        return tag

# some common namespaces we use
RDFNS = XMLNamespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
DCNS = XMLNamespace('http://purl.org/dc/elements/1.1/')
MARCRELNS = XMLNamespace('http://www.loc.gov/loc.terms/relators/')

XINS = XMLNamespace("http://www.w3.org/2001/XInclude")
XHTMLNS = XMLNamespace("http://www.w3.org/1999/xhtml")

common_uris = {
    RDFNS.uri: 'rdf',
    DCNS.uri: 'dc',
    MARCRELNS.uri: 'marcrel',
}

common_prefixes = dict((i[1], i[0]) for i in common_uris.items())

class NamespaceProxy(object):

    def __init__(self, desc, uri):
        object.__setattr__(self, 'uri', uri)
        object.__setattr__(self, 'desc', desc)

    def __getattr__(self, key):
        return object.__getattribute__(self, 'desc')[self.uri, key]

    def __setattr__(self, key, value):
        object.__getattribute__(self, 'desc')[self.uri, key] = value

    def __iter__(self):
        return ((XMLNamespace.tagname(attr.schema.name), attr.value) for attr in object.__getattribute__(self, 'desc').attrs.filter(schema__name__startswith="{%s}" % self.uri))

class NamespaceDescriptor(object):

    def __init__(self, nsuri):
        self.nsuri = nsuri

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return NamespaceProxy(instance, self.nsuri)

    def __set__(self, instance, value):
        raise ValueError



