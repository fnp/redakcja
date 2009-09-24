# -*- encoding: utf-8 -*-
__author__="Łukasz Rekucki"
__date__ ="$2009-09-18 10:49:24$"

__doc__ = """Main module for the Repository Abstraction Layer"""

class Library(object):

    def __init__(self, create=False):
        """Open an existing library, or create a new one. By default, fails if
        the library doesn't exist."""
        self.create = create     
        
    def main_cabinet(self):
        """Return the "main" cabinet of the library."""
        pass

    def cabinets(self):
        """List all cabinets in the library."""
        pass

    def cabinet(self, document, user, create=False):
        """Open a cabinet belonging to the _user_ for a given _document_.
        If the _document_ is actually a sub-document, it's parent's cabinet is
        opened istead.
        
        If the cabinet doesn't exists and create is False (the default), a 
        CabinetNotFound exception is raised.
        
        If create is True, a new cabinet is created if it doesn't exist yet."""
        pass


class Cabinet(object):

    def __init__(self, library, name=None, doc=None, user=None):
        self._library = library
        if name:
            self._name = name
            self._maindoc = ''
            self._user = self._document = None
        elif doc and user:
            self._user = user
            self._document = doc
            self._name = user + ':' + doc
            self._maindoc = doc
        else:
            raise ValueError("You must provide either name or doc and user.")

        print "new cab:", self._name, self._user, self._document

    @property
    def username(self):
        return self._user

    def __str__(self):
        return "Cabinet(%s)" % self._name

    def documents(self):
        """Lists all documents and sub-documents in this cabinet."""
        pass
    
    def retrieve(self, parts=None, shelve=None):
        """Retrieve a document from a given shelve in the cabinet. If no
        part is given, the main document is retrieved. If no shelve is given,
        the top-most shelve is used.

        If parts is a list, all the given parts are retrieved atomicly. Use None
        as the name for the main document"""
        pass

    def create(self, name, initial_data=''):
        """Create a new sub-document in the cabinet with the given name."""
        pass

    @property
    def maindoc_name(self):
        return self._maindoc

    @property
    def library(self):
        return self._library

    @property
    def name(self):
        return self._name

    def shelf(self, selector=None):
        pass

class Document(object):
    def __init__(self, cabinet, name):
        self._cabinet = cabinet
        self._name = name

    def read(self):
        pass

    def write(self, data):
        pass

    @property
    def cabinet(self):
        return self._cabinet

    @property
    def library(self):
        return self._cabinet.library

    @property
    def name(self):
        return self._name

    def shelf(self):
        return self._cabinet.shelf()

    @property
    def size(self):
        raise NotImplemented()

    @property
    def parts(self):
        raise NotImplemented()


class Shelf(object):

    def __init__(self, lib):
        self._library = lib        
    
#
# Exception classes
#

class LibraryException(Exception):
    
    def __init__(self, msg, cause=None):
        Exception.__init__(self, msg)
        self.cause = cause

class CabinetNotFound(LibraryException):
    def __init__(self, cabname):
        LibraryException.__init__(self, "Cabinet '%s' not found." % cabname)
    pass


# import backends to local namespace
from backend_mercurial import MercurialLibrary