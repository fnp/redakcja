# -*- encoding: utf-8 -*-
__author__ = "Łukasz Rekucki"
__date__ = "$2009-09-18 10:49:24$"

__doc__ = """RAL implementation over Mercurial"""

import mercurial
from mercurial import localrepo as hglrepo
from mercurial import ui as hgui
import re
import wlrepo

FILTER = re.compile(r"^pub_(.+)\.xml$", re.UNICODE)

def default_filter(name):
    m = FILTER.match(name)    
    if m is not None:
        return name, m.group(1)
    return None

class MercurialLibrary(wlrepo.Library):

    def __init__(self, path, maincabinet="default", ** kwargs):
        super(wlrepo.Library, self).__init__( ** kwargs)

        self._hgui = hgui.ui()
        self._hgui.config('ui', 'quiet', 'true')
        self._hgui.config('ui', 'interactive', 'false')

        import os.path        
        self._ospath = self._sanitize_string(os.path.realpath(path))
        
        maincabinet = self._sanitize_string(maincabinet)

        if os.path.isdir(path):
            try:
                self._hgrepo = hglrepo.localrepository(self._hgui, path)
            except mercurial.error.RepoError:
                raise wlrepo.LibraryException("[HGLibrary]Not a valid repository at path '%s'." % path)
        elif kwargs['create']:
            os.makedirs(path)
            try:
                self._hgrepo = hglrepo.localrepository(self._hgui, path, create=1)
            except mercurial.error.RepoError:
                raise wlrepo.LibraryException("[HGLibrary] Can't create a repository on path '%s'." % path)
        else:
            raise wlrepo.LibraryException("[HGLibrary] Can't open a library on path '%s'." % path)

        # fetch the main cabinet
        lock = self._hgrepo.lock()
        try:
            btags = self._hgrepo.branchtags()
            
            if not self._has_branch(maincabinet):
                raise wlrepo.LibraryException("[HGLibrary] No branch named '%s' to init main cabinet" % maincabinet)
        
            self._maincab = MercurialCabinet(self, maincabinet)
        finally:
            lock.release()

    @property
    def main_cabinet(self):
        return self._maincab

    def cabinet(self, docid, user, create=False):
        bname = self._bname(user, docid)

        lock = self._lock(True)
        try:
            if self._has_branch(bname):
                return MercurialCabinet(self, bname, doc=docid, user=user)

            if not create:
                raise wlrepo.CabinetNotFound(docid, user)

            # check if the docid exists in the main cabinet
            needs_touch = not self._maincab.exists(docid)
            print "Creating branch: ", needs_touch
            cab = MercurialCabinet(self, bname, doc=docid, user=user)

            fileid = cab._fileid(None)

            def cleanup_action(l):
                if needs_touch:
                    print "Touch for file", docid
                    l._fileopener()(fileid, "w").write('')
                    l._fileadd(fileid)
                
                garbage = [fid for (fid, did) in l._filelist() if not did.startswith(docid)]
                print "Garbage: ", garbage
                l._filesrm(garbage)

            # create the branch
            self._create_branch(bname, before_commit=cleanup_action)
            return MercurialCabinet(self, bname, doc=docid, user=user)
        finally:
            lock.release()
            
    #
    # Private methods
    #

    #
    # Locking
    #
 
    def _lock(self, write_mode=False):
        return self._hgrepo.wlock() # no support for read/write mode yet

    def _transaction(self, write_mode, action):
        lock = self._lock(write_mode)
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

    def _commit(self, message, user="library"):
        return self._hgrepo.commit(\
                                   text=self._sanitize_string(message), \
                                   user=self._sanitize_string(user))


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

    def _filelist(self, filter=default_filter):
        for name in  self._hgrepo[None]:
            result = filter(name)
            if result is None: continue
            
            yield result

    def _fileopener(self):
        return self._hgrepo.wopener
    
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
            parent = self._maincab

        parentrev = parent._hgtip()

        self._checkout(parentrev)
        self._hgrepo.dirstate.setbranch(name)

        if before_commit: before_commit(self)

        print "commiting"
        self._commit("[AUTO] Initial commit for branch '%s'." % name, user='library')
        
        # revert back to main
        self._checkout(self._maincab._hgtip())
        return self._branch_tip(name)

    def _switch_to_branch(self, branchname):
        current = self._hgrepo[None].branch()

        if current == branchname:
            return current # quick exit
        
        self._checkout(self._branch_tip(branchname))
        return branchname        

    #
    # Merges
    #
    


    #
    # Utils
    #

    @staticmethod
    def _sanitize_string(s):
        if isinstance(s, unicode): #
            return s.encode('utf-8')
        else: # it's a string, so we have no idea what encoding it is
            return s

class MercurialCabinet(wlrepo.Cabinet):
    
    def __init__(self, library, branchname, doc=None, user=None):
        if doc and user:
            super(MercurialCabinet, self).__init__(library, doc=doc, user=user)
        else:
            super(MercurialCabinet, self).__init__(library, name=branchname)
            
        self._branchname = branchname

    def documents(self):        
        return self._execute_in_branch(action=lambda l, c: ( e[1] for e in l._filelist()) )

    def retrieve(self, part=None, shelve=None):
        fileid = self._fileid(part)

        if fileid is None:
            raise wlrepo.LibraryException("Can't retrieve main document from main cabinet.")
                
        return self._execute_in_branch(lambda l, c: MercurialDocument(c, fileid))

    def create(self, name, initial_data=''):
        fileid = self._fileid(name)

        if name is None:
            raise ValueError("Can't create main doc for maincabinet.")

        def create_action(l, c):
            if l._fileexists(fileid):
                raise wlrepo.LibraryException("Can't create document '%s' in cabinet '%s' - it already exists" % (fileid, c.name))

            fd = l._fileopener()(fileid, "w")
            fd.write(initial_data)
            l._fileadd(fileid)
            l._commit("File '%d' created.")

            return MercurialDocument(c, fileid)

        return self._execute_in_branch(create_action)

    def exists(self, part=None, shelve=None):
        fileid = self._fileid(part)

        if fileid is None: return false
        return self._execute_in_branch(lambda l, c: l._fileexists(fileid))
    
    def _execute_in_branch(self, action, write=False):
        def switch_action(library):
            old = library._switch_to_branch(self._branchname)
            try:
                return action(library, self)
            finally:
                library._switch_to_branch(old)

        return self._library._transaction(write_mode=write, action=switch_action)

    def _fileid(self, part):
        fileid = None

        if self._maindoc == '':
            if part is None: return None              
            fileid = part
        else:
            fileid = self._maindoc + (('$' + part) if part else '')

        return 'pub_' + fileid + '.xml'        

    def _fileopener(self):
        return self._library._fileopener()

    def _hgtip(self):
        return self._library._branch_tip(self._branchname)

class MercurialDocument(wlrepo.Document):

    def __init__(self, cabinet, fileid):
        super(MercurialDocument, self).__init__(cabinet, fileid)
        self._opener = self._cabinet._fileopener()        

    def read(self):
        return self._opener(self._name, "r").read()

    def write(self, data):
        return self._opener(self._name, "w").write(data)


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


__all__ = ["MercurialLibrary", "MercurialCabinet", "MercurialDocument"]