# -*- encoding: utf-8 -*-
__author__="Łukasz Rekucki"
__date__ ="$2009-09-18 10:49:24$"
__doc__ = """Main module for the Repository Abstraction Layer"""

class Library(object):

    def __init__(self, create=False):
        """Open an existing library, or create a new one. By default, fails if
        the library doesn't exist."""
        self.create = create      

    def documents(self):
        """List all documents in the library."""
        pass

    def document_for_rev(self, rev):
        """Retrieve a document in the specified revision."""
        pass

    def document(self, docid, user=None):
        """Retrieve a document from a library."""
        pass

    def get_revision(self, revid):
        """Retrieve a handle to a specified revision."""
        return None

    def document_create(self, docid):
        """Create a new document. The document will have it's own branch."""
        

class Document(object):
    """A class representing a document package boundled with a revision."""

    def __init__(self, library, revision):
        """_library_ should be an instance of a Library."""
        self._library = library
        if isinstance(revision, Revision):
            self._revision = revision
        else:
            self._revision = library.get_revision(revision)


    def take(self, user):
        """Make a user copy of the document. This is persistant."""
        pass

    def giveback(self):
        """Informs the library, that the user no longer needs this document.
        Should be called on the user version of document. If not, it doesn nothing."""
       
    def data(self, entry):
        """Returns the specified entry as a file-like object."""
        pass

    @property
    def library(self):
        return self._library

    @property
    def revision(self):
        return self._revision

    @property
    def id(self):
        return self._revision.document_name

    @property
    def owner(self):
        return self._revision.user_name
    
    def parentof(self, other):
        return self._revision.parentof(other._revision)

    def ancestorof(self, other):
        return self._revision.ancestorof(other._revision)


class Revision(object):

    def __init__(self, lib):
        self._library = lib

    def parentof(self, other):
        return False

    def ancestorof(self, other):
        return False

    @property
    def document_name(self):
        raise ValueError()

    @property
    def user_name(self):
        raise ValueError()

#
# Exception classes
#

class LibraryException(Exception):    
    def __init__(self, msg, cause=None):
        Exception.__init__(self, msg)
        self.cause = cause

class RevisionNotFound(LibraryException):
    def __init__(self, rev):
        LibraryException.__init__(self, "Revision %r not found." % rev)
    pass

class DocumentAlreadyExists(LibraryException):
    pass

# import backends to local namespace
from mercurial_backend.library import MercurialLibrary