# -*- coding: utf-8 -*-
import os
from mercurial import localrepo, ui, encoding, util
import mercurial.merge, mercurial.error

encoding.encoding = 'utf-8'

X = 'g\xc5\xbceg\xc5\xbc\xc3\xb3\xc5\x82ka'

def sanitize_string(path):
    if isinstance(path, unicode): #
        return path.encode('utf-8')
    else: # it's a string, so we have no idea what encoding it is
        return path

class Repository(object):
    """Abstrakcja repozytorium Mercurial. Działa z Mercurial w wersji 1.3.1."""
    
    def __init__(self, path, create=False):
        self.ui = ui.ui()
        self.ui.config('ui', 'quiet', 'true')
        self.ui.config('ui', 'interactive', 'false')
        
        self.real_path = sanitize_string(os.path.realpath(path))
        self.repo = self._open_repository(self.real_path, create)

    def _open_repository(self, path, create=False):
        if os.path.isdir(path):
            try:
                return localrepo.localrepository(self.ui, path)
            except mercurial.error.RepoError:
                # dir is not an hg repo, we must init it
                if create:
                    return localrepo.localrepository(self.ui, path, create=1)
        elif create:
            os.makedirs(path)
            return localrepo.localrepository(self.ui, path, create=1)
        raise RepositoryDoesNotExist("Repository %s does not exist." % path)
        
    def file_list(self, branch):
        return self.in_branch(lambda: self._file_list(), branch)

    def _file_list(self):
        return list(self.repo[None])
    
    def get_file(self, path, branch):
        return self.in_branch(lambda: self._get_file(path), branch)

    def _get_file(self, path):
        path = sanitize_string(path)
        if not self._file_exists(path):
            raise RepositoryException("File not availble in this branch.")
        
        return self.repo.wread(path)

    def file_exists(self, path, branch):
        return self.in_branch(lambda: self._file_exists(path), branch)

    def _file_exists(self, path):
        path = sanitize_string(path)
        return self.repo.dirstate[path] != "?"

    def write_file(self, path, value, branch):
        return self.in_branch(lambda: self._write_file(path, value), branch)

    def _write_file(self, path, value):
        path = sanitize_string(path)
        return self.repo.wwrite(path, value, [])

    def add_file(self, path, value, branch):
        return self.in_branch(lambda: self._add_file(path, value), branch)

    def _add_file(self, path, value):
        path = sanitize_string(path)
        self._write_file(path, value)
        return self.repo.add( [path] )

    def _commit(self, message, user=None):
        return self.repo.commit(text=sanitize_string(message), user=sanitize_string(user))
    
    def commit(self, message, branch, user=None):
        return self.in_branch(lambda: self._commit(message, key=key, user=user), branch)

    def in_branch(self, action, bname):
        wlock = self.repo.wlock()
        try:
            old = self._switch_to_branch(bname)
            try:
                # do some stuff
                return action()
            finally:
                self._switch_to_branch(old)
        finally:
            wlock.release()

    def merge_branches(self, bnameA, bnameB, user, message):
        wlock = self.repo.wlock()
        try:
            return self.merge_revisions(self.get_branch_tip(bnameA),
                self.get_branch_tip(bnameB), user, message)
        finally:
            wlock.release()

    def diff(self, revA, revB):
        return UpdateStatus(self.repo.status(revA, revB))

    def merge_revisions(self, revA, revB, user, message):
        wlock = self.repo.wlock()
        try:
            old = self.repo[None]
            
            self._checkout(revA)
            mergestatus = self._merge(revB)
            if not mergestatus.isclean():
                # revert the failed merge
                self.repo.recover()
                raise UncleanMerge(u'Failed to merge %d files.' % len(mergestatus.unresolved))

            # commit the clean merge
            self._commit(message, user)

            # cleanup after yourself
            self._checkout(old.rev())
        except util.Abort, ae:
            raise RepositoryException(u'Failed merge: ' + ae.message)
        finally:
            wlock.release()

    def common_ancestor(self, revA, revB):
        return self.repo[revA].ancestor(self.repo[revB])
        
    def _checkout(self, rev, force=True):
        return MergeStatus(mercurial.merge.update(self.repo, rev, False, force, None))
        
    def _merge(self, rev):
        """ Merge the revision into current working directory """
        return MergeStatus(mercurial.merge.update(self.repo, rev, True, False, None))

    def _switch_to_branch(self, bname):
        bname = sanitize_string(bname)
        wlock = self.repo.wlock()
        try:
            current = self.repo[None].branch()
            if current == bname:
                return current
            
            tip = self.get_branch_tip(bname)
            status = self._checkout(tip)

            if not status.isclean():
                raise RepositoryException("Unclean branch switch. This IS REALLY bad.")
            
            return current 
        except KeyError, ke:
            raise RepositoryException((u"Can't switch to branch '%s': no such branch." % bname) , ke)
        except util.Abort, ae:
            raise RepositoryException(u"Can't switch to branch '%s': %s"  % (bname, ae.message), ae)
        finally:
            wlock.release()

    def with_wlock(self, action):
        wlock = self.repo.wlock()
        try:
            action()
        finally:
            wlock.release()

    def _create_branch(self, name, parent_rev, msg=None, before_commit=None):
        """WARNING: leaves the working directory in the new branch"""
        name = sanitize_string(name)
        
        if self.has_branch(name): return # just exit

        self._checkout(parent_rev)
        self.repo.dirstate.setbranch(name)
        
        if msg is None:
            msg = "Initial commit for branch '%s'." % name

        if before_commit: before_commit()        
        self._commit(msg, user='platform')
        return self.get_branch_tip(name)

    def write_lock(self):
        """Returns w write lock to the repository."""
        return self.repo.wlock()

    def has_branch(self, name):
        name = sanitize_string(name)
        return (name in self.repo.branchmap().keys())
    
    def get_branch_tip(self, name):
        name = sanitize_string(name)
        return self.repo.branchtags()[name]

    def getnode(self, rev):
        return self.repo[rev]

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
        return bool( len(self.modified) + len(self.added) + \
            len(self.removed) + len(self.deleted) )

class RepositoryException(Exception):
    def __init__(self, msg, cause=None):
        Exception.__init__(self, msg)
        self.cause = cause

class UncleanMerge(RepositoryException):
    pass

class RepositoryDoesNotExist(RepositoryException):
    pass

