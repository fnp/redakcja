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
        
    def all_files(self, branch='default'):
        return self.in_branch(lambda: self._all_files(), branch)

    def _all_files(self):
        return list(self.repo[None])
    
    def get_file(self, path, branch='default'):
        return self.in_branch(lambda: self._get_file(path), branch)

    def _get_file(self, path):
        return self.repo.wread(path)
    
    def add_file(self, path, value, branch='default'):
        return self.in_branch(lambda: self._add_file(path, value), branch)

    def _add_file(self, path, value):
        return self.repo.wwrite(path, value.encode('utf-8'), [])
#        f = codecs.open(os.path.join(self.real_path, path), 'w', encoding='utf-8')
#        f.write(value)
#        f.close()
#        if path not in self._pending_files:
#            self._pending_files.append(path)

    def _commit(self, message, user=None, key=None):
        return self.repo.commit(text=message, user=user)
    
    def _commit2(self, message, key=None, user=None):
        """
        Commit unsynchronized data to disk.
        Arguments::

         - message: mercurial's changeset message
         - key: supply to sync only one key
        """
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        if isinstance(user, unicode):
            user = user.encode('utf-8')
        
        commited = False
        rev = None
        files_to_add = []
        files_to_remove = []
        files_to_commit = []

        # first of all, add absent data and clean removed
        if key is None:
            # will commit all keys
            pending_files = self._pending_files
        else:
            if keys not in self._pending_files:
                # key isn't changed
                return None
            else:
                pending_files = [key]
        for path in pending_files:
            files_to_commit.append(path)
            if path in self.all_files():
                if not os.path.exists(os.path.join(self.real_path, path)):
                    # file removed
                    files_to_remove.append(path)
            else:
                # file added
                files_to_add.append(path)
        # hg add
        if files_to_add:
            self.repo.add(files_to_add)
        # hg forget
        if files_to_remove:
            self.repo.forget(files_to_remove)
        # ---- hg commit
        if files_to_commit:
            for i, f in enumerate(files_to_commit):
                if isinstance(f, unicode):
                    files_to_commit[i] = f.encode('utf-8')
            matcher = match.match(self.repo.root, self.repo.root, files_to_commit, default='path')
            rev = self.repo.commit(message, user=user, match=matcher)
            commited = True
        # clean pending keys
        for key in pending_files:
            self._pending_files.remove(key)
        # if commited:
            # reread keys
            # self._keys = self.get_persisted_objects_keys()
            # return node.hex(rev)

    def commit(self, message, key=None, user=None, branch='default'):
        return self.in_branch(lambda: self._commit(message, key=key, user=user), branch)

    def in_branch(self, action, bname='default'):
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

    def _switch_to_branch(self, bname):
        wlock = self.repo.wlock()
        try:
            current = self.repo[None].branch()
            if current == bname:
                return current

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
