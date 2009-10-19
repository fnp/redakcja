# -*- encoding: utf-8 -*-

import logging
log = logging.getLogger('ral.mercurial')

__author__ = "Łukasz Rekucki"
__date__ = "$2009-09-25 09:35:06$"
__doc__ = "Module documentation."

import wlrepo
import mercurial.error
import re

import logging
log = logging.getLogger('wlrepo.document')

class MercurialDocument(wlrepo.Document):

    def data(self, entry):
        path = self._library._sanitize_string(self.id + u'.' + entry)
        try:
            return self._library._filectx(path, \
                self._revision.hgrev()).data().decode('utf-8')
        except mercurial.error.LookupError, e:
            fl = [x.decode('utf-8') for x in self._revision._changectx]            
            raise wlrepo.EntryNotFound(self._revision, path.decode('utf-8'), fl)

    def quickwrite(self, entry, data, msg, user=None):
        user = user or self.owner

        if isinstance(data, unicode):
            data = data.encode('utf-8')
            
        user = self._library._sanitize_string(user)
        msg = self._library._sanitize_string(msg)
        entry = self._library._sanitize_string(entry)

        if user is None:
            raise ValueError("Can't determine user.")
        
        def write(l, r):
            f = l._fileopen(r(entry), "w+")
            f.write(data)
            f.close()
            l._fileadd(r(entry))            

        return self.invoke_and_commit(write, lambda d: (msg, \
                self._library._sanitize_string(self.owner)) )

    def invoke_and_commit(self, ops, commit_info):
        lock = self._library.lock()
        try:            
            self._library._checkout(self._revision.hgrev())

            def entry_path(entry):
                return self._library._sanitize_string(self.id + u'.' + entry)
            
            ops(self._library, entry_path)
            message, user = commit_info(self)

            message = self._library._sanitize_string(message)
            user = self._library._sanitize_string(user)

            self._library._commit(message, user)
            try:
                return self._library.document(docid=self.id, user=user)
            except Exception, e:
                # rollback the last commit
                self._library._rollback()
                raise e
        finally:
            lock.release()
        
    # def commit(self, message, user):
    #    """Make a new commit."""
    #    self.invoke_and_commit(message, user, lambda *a: True)

    def ismain(self):
        return self._revision.user_name is None

    def islatest(self):
        return (self == self.latest())

    def shared(self):
        if self.ismain():
            return self
        
        return self._library.document(docid=self.id)

    def latest(self):
        return self._library.document(docid=self.id, user=self.owner)

    def take(self, user):
        fullid = self._library.fulldocid(self.id, user)

        def take_action(library, resolve):
            # branch from latest 
            library._set_branchname(fullid)

        if not self._library.has_revision(fullid):
            log.info("Checking out document %s" % fullid)

            self.invoke_and_commit(take_action, \
                lambda d: ("$AUTO$ File checkout.", user) )

        return self._library.document_for_rev(fullid)

    def up_to_date(self):
        return self.ismain() or (\
            self.shared().ancestorof(self) )
        
            
    def update(self, user):
        """Update parts of the document."""
        lock = self.library.lock()
        try:
            if self.ismain():
                # main revision of the document
                return self
            
            if self._revision.has_children():                
                raise UpdateException("Revision has children.")

            sv = self.shared()

            if self.parentof(sv):
                return self

            if sv.ancestorof(self):
                return self

            if self._revision.merge_with(sv._revision, user=user,\
                message="$AUTO$ Personal branch update."):
                return self.latest()
            else:
                raise UpdateException("Merge failed.")
        finally:
            lock.release()  

    def share(self, message):
        lock = self.library.lock()
        try:            
            if self.ismain():
                return False # always shared

            user = self._revision.user_name
            main = self.shared()._revision
            local = self._revision            

            # Case 1:
            #         * local
            #         |
            #         * <- can also be here!
            #        /|
            #       / |
            # main *  *
            #      |  |
            # The local branch has been recently updated,
            # so we don't need to update yet again, but we need to
            # merge down to default branch, even if there was
            # no commit's since last update
            #
            # This is actually the only good case!
            if main.ancestorof(local):
                success, changed = main.merge_with(local, user=user, message=message)

                if not success:
                    raise LibraryException("Merge failed.")

                return changed
            
            # Case 2:
            # main *
            #      |
            #      * <- this case overlaps with previos one
            #      |\
            #      | \
            #      |  * local
            #      |  |
            #
            # There was a recent merge to the defaul branch and
            # no changes to local branch recently.
            #
            # Nothing to do
            elif local.ancestorof(main):                
                return False

            # In all other cases, the local needs an update
            # and possibly conflict resolution, so fail
            raise LibraryExcepton("Document not prepared for sharing.")
        
        finally:
            lock.release()


    def has_conflict_marks(self):
        return re.search("^(?:<<<<<<< .*|=======|>>>>>>> .*)$", self.data('xml'), re.MULTILINE)        

    def __unicode__(self):
        return u"Document(%s:%s)" % (self.id, self.owner)

    def __str__(self):
        return self.__unicode__().encode('utf-8')
    
    def __eq__(self, other):
        return (self._revision == other._revision)

