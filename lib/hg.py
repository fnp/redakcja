# -*- coding: utf-8 -*-
import os
import codecs
from mercurial import localrepo, ui, match, node, encoding, util
import mercurial.merge, mercurial.error

encoding.encoding = 'utf-8'


class RepositoryDoesNotExist(Exception):
    pass

class Repository(object):
    """Abstrakcja repozytorium Mercurial. Działa z Mercurial w wersji 1.3.1."""
    
    def __init__(self, path, create=False):
        self.ui = ui.ui()
        self.ui.config('ui', 'quiet', 'true')
        self.ui.config('ui', 'interactive', 'false')
        
        self.real_path = os.path.realpath(path)
        self.repo = self.open_repository(self.real_path, create)
        self._pending_files = []
    
    def open_repository(self, path, create=False):
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
        return self.repo.wread(path)
    
    def add_file(self, path, value, branch):
        return self.in_branch(lambda: self._add_file(path, value), branch)

    def _add_file(self, path, value):
        return self.repo.wwrite(path, value.encode('utf-8'), [])

    def _commit(self, message, user=None):
        return self.repo.commit(text=message, user=user)
    
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

    def _switch_to_branch(self, bname, create=True):
        wlock = self.repo.wlock()
        try:
            current = self.repo[None].branch()
            if current == bname:
                return current
            try:
                tip = self.repo.branchtags()[bname]
            except KeyError, ke:
                if not create: raise ke
                
                # create the branch on the fly

                # first switch to default branch
                default_tip = self.repo.branchtags()['default']
                mercurial.merge.update(self.repo, default_tip, False, True, None)

                # set the dirstate to new branch
                self.repo.dirstate.setbranch(bname)
                self._commit('Initial commit for automatic branch "%s".' % bname, user="django-admin")

                # collect the new tip
                tip = self.repo.branchtags()[bname]

            upstats = mercurial.merge.update(self.repo, tip, False, True, None)
            return current
        except KeyError, ke:
            raise RepositoryException("Can't switch to branch '%s': no such branch." % bname , ke)
        except util.Abort, ae:
            raise repositoryException("Can't switch to branch '%s': %s"  % (bname, ae.message), ae)
        finally:
            wlock.release()

    def write_lock(self):
        """Returns w write lock to the repository."""
        return self.repo.wlock()


class RepositoryException(Exception):

    def __init__(self, msg, cause=None):
        Exception.__init__(self, msg)
        self.cause = cause
