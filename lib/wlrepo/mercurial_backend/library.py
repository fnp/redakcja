# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 09:33:02$"
__doc__ = "Module documentation."

import mercurial
from mercurial import localrepo as hglrepo
from mercurial import ui as hgui
from mercurial import error
import wlrepo

from wlrepo.mercurial_backend.document import MercurialDocument
from wlrepo.mercurial_backend import MercurialRevision

class MergeStatus(object):
    def __init__(self, mstatus):
        self.updated = mstatus[0]
        self.merged = mstatus[1]
        self.removed = mstatus[2]
        self.unresolved = mstatus[3]

    def isclean(self):
        return self.unresolved == 0

class UpdateStatus(object):

    def __init__(self, mstatus):
        self.modified = mstatus[0]
        self.added = mstatus[1]
        self.removed = mstatus[2]
        self.deleted = mstatus[3]
        self.untracked = mstatus[4]
        self.ignored = mstatus[5]
        self.clean = mstatus[6]

    def has_changes(self):
        return bool(len(self.modified) + len(self.added) + \
                    len(self.removed) + len(self.deleted))

class MercurialLibrary(wlrepo.Library):
    """Mercurial implementation of the Library API"""

    def __init__(self, path, **kwargs):
        super(wlrepo.Library, self).__init__( ** kwargs)

        self._revcache = {}
        self._doccache = {}

        self._hgui = hgui.ui()
        self._hgui.config('ui', 'quiet', 'true')
        self._hgui.config('ui', 'interactive', 'false')

        import os.path
        self._ospath = self._sanitize_string(os.path.realpath(path))        

        if os.path.isdir(path):
            try:
                self._hgrepo = hglrepo.localrepository(self._hgui, path)
            except mercurial.error.RepoError:
                raise wlrepo.LibraryException("[HGLibrary] Not a valid repository at path '%s'." % path)
        elif kwargs.get('create', False):
            os.makedirs(path)
            try:
                self._hgrepo = hglrepo.localrepository(self._hgui, path, create=1)
            except mercurial.error.RepoError:
                raise wlrepo.LibraryException("[HGLibrary] Can't create a repository on path '%s'." % path)
        else:
            raise wlrepo.LibraryException("[HGLibrary] Can't open a library on path '%s'." % path)


    def documents(self):
        return [ key[5:] for key in \
            self._hgrepo.branchmap() if key.startswith("$doc:") ]

    @property
    def ospath(self):
        return self._ospath

    def document_for_rev(self, revision):
        if revision is None:
            raise ValueError("Revision can't be None.")
        
        if not isinstance(revision, MercurialRevision):
            rev = self.get_revision(revision)
        else:
            rev = revision       

        if not self._doccache.has_key(str(rev)):
            self._doccache[str(rev)] = MercurialDocument(self, rev)

        # every revision is a document
        return self._doccache[str(rev)]

    def document(self, docid, user=None):       
        return self.document_for_rev(self.fulldocid(docid, user))

    def get_revision(self, revid):
        revid = self._sanitize_string(revid)
        
        ctx = self._changectx(revid)

        if ctx is None:
            raise RevisionNotFound(revid)

        if self._revcache.has_key(ctx):
            return self._revcache[ctx]

        return MercurialRevision(self, ctx)

    def fulldocid(self, docid, user=None):
        docid = self._sanitize_string(docid)
        user = self._sanitize_string(user)
        
        fulldocid = ''
        if user is not None:
            fulldocid += '$user:' + user
        fulldocid += '$doc:' + docid
        return fulldocid


    def has_revision(self, revid):
        try:
            self._hgrepo[revid]
            return True
        except error.RepoError:
            return False

    def document_create(self, docid):
        docid = self._sanitize_string(docid)
        
        # check if it already exists
        fullid = self.fulldocid(docid)

        if self.has_revision(fullid):
            raise wlrepo.DocumentAlreadyExists("Document %s already exists!" % docid);

        # doesn't exist
        self._create_branch(fullid)
        return self.document_for_rev(fullid)

    #
    # Private methods
    #

    #
    # Locking
    #

    def lock(self, write_mode=False):
        return self._hgrepo.wlock() # no support for read/write mode yet

    def _transaction(self, write_mode, action):
        lock = self.lock(write_mode)
        try:
            return action(self)
        finally:
            lock.release()

    #
    # Basic repo manipulation
    #

    def _checkout(self, rev, force=True):
        return MergeStatus(mercurial.merge.update(self._hgrepo, rev, False, force, None))

    def _merge(self, rev):
        """ Merge the revision into current working directory """
        return MergeStatus(mercurial.merge.update(self._hgrepo, rev, True, False, None))

    def _common_ancestor(self, revA, revB):
        return self._hgrepo[revA].ancestor(self.repo[revB])

    def _commit(self, message, user=u"library"):
        return self._hgrepo.commit(text=message, user=user)


    def _fileexists(self, fileid):
        return (fileid in self._hgrepo[None])

    def _fileadd(self, fileid):
        return self._hgrepo.add([fileid])

    def _filesadd(self, fileid_list):
        return self._hgrepo.add(fileid_list)

    def _filerm(self, fileid):
        return self._hgrepo.remove([fileid])

    def _filesrm(self, fileid_list):
        return self._hgrepo.remove(fileid_list)   

    def _fileopen(self, path, mode):
        return self._hgrepo.wopener(path, mode)

    def _filectx(self, fileid, revid):
        return self._hgrepo.filectx(fileid, changeid=revid)

    def _changectx(self, nodeid):
        return self._hgrepo.changectx(nodeid)

    def _rollback(self):
        return self._hgrepo.rollback()

    #
    # BASIC BRANCH routines
    #

    def _bname(self, user, docid):
        """Returns a branch name for a given document and user."""
        docid = self._sanitize_string(docid)
        uname = self._sanitize_string(user)
        return "personal_" + uname + "_file_" + docid;

    def _has_branch(self, name):
        return self._hgrepo.branchmap().has_key(self._sanitize_string(name))

    def _branch_tip(self, name):
        name = self._sanitize_string(name)
        return self._hgrepo.branchtags()[name]    

    def _create_branch(self, name, parent=None, before_commit=None):
        name = self._sanitize_string(name)

        if self._has_branch(name): return # just exit

        if parent is None:
            parentrev = self._hgrepo['$branchbase'].node()
        else:
            parentrev = parent.hgrev()

        self._checkout(parentrev)
        self._hgrepo.dirstate.setbranch(name)

        if before_commit: before_commit(self)

        self._commit("$ADMN$ Initial commit for branch '%s'." % name, user='$library')        

    def _switch_to_branch(self, branchname):
        current = self._hgrepo[None].branch()

        if current == branchname:
            return current # quick exit

        self._checkout(self._branch_tip(branchname))
        return branchname    

    #
    # Utils
    #

    @staticmethod
    def _sanitize_string(s):
        if s is None:
            return None

        if isinstance(s, unicode):
            s = s.encode('utf-8')        

        return s