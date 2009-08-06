# -*- coding: utf-8 -*-
import os
import codecs
from mercurial import localrepo, ui, error, match, node


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
            except error.RepoError:
                # dir is not an hg repo, we must init it
                if create:
                    return localrepo.localrepository(self.ui, path, create=1)
        elif create:
            os.makedirs(path)
            return localrepo.localrepository(self.ui, path, create=1)
        raise RepositoryDoesNotExist("Repository %s does not exist." % path)
        
    def all_files(self):
        return list(self.repo['tip'])
    
    def get_file(self, path):
        ctx = self.repo.changectx(None)
        return ctx.filectx(path)
    
    def add_file(self, path, value):
        f = codecs.open(os.path.join(self.real_path, path), 'w', encoding='utf-8')
        f.write(value)
        f.close()

        if path not in self._pending_files:
            self._pending_files.append(path)
    
    def commit(self, message='hgshelve auto commit', key=None, user=None):
        """
        Commit unsynchronized data to disk.
        Arguments::

         - message: mercurial's changeset message
         - key: supply to sync only one key
        """
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
            if key not in self._pending_files:
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
            