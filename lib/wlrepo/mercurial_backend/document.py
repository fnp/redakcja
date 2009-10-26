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

        return self._library.document_for_revision(fullid)

    def up_to_date(self):
        if self.ismain():
            return True

        shared = self.shared()
        
        if shared.ancestorof(self):
            return True

        if shared.has_parent_from(self):
            return True

        return False
                    
    def update(self, user):
        """Update parts of the document."""
        lock = self.library.lock()
        try:
            if self.ismain():
                # main revision of the document
                return self

            # check for children in this branch
            if self._revision.has_children(limit_branch=True):
                raise wlrepo.UpdateException("Revision %s has children." % self.revision)

            shared = self.shared()
            #     *
            #    /|
            #   * |
            #   | |
            #
            # we carry the latest version
            if shared.ancestorof(self):
               return self

            #   *
            #   |\
            #   | *
            #   | |
            #
            # We just shared
            if self.parentof(shared):
                return self

            #  s     s  S
            #  |     |  |
            #  *<-S  *<-*
            #  |  |  |  .
            #
            #  This is ok (s - shared, S - self)

            if self._revision.merge_with(shared._revision, user=user,\
                message="$AUTO$ Personal branch update."):
                return self.latest()
            else:
                raise wlrepo.UpdateException("Merge failed.")
        finally:
            lock.release()


    def would_share(self):
        if self.ismain():
            return False, "Main version is always shared"

        shared = self.shared()

        # we just did this - move on
        if self.parentof(shared):
            return False, "Document has been recetly shared - no changes"

        #     *
        #    /|
        #   * *
        #   |\|
        #   | *
        #   | |
        # Situation above is ok - what we don't want, is:
        #     *
        #    /|
        #   * |
        #   |\|
        #   | *
        #   | |
        # We want to prevent stuff like this.
        if self.parent().parentof(shared) and shared.parentof(self):
            return False, "Preventing zig-zag"

        return True, "All ok"

    def share(self, message):
        lock = self.library.lock()
        try:
            # check if the document is in "updated" state
            if not self.up_to_date():
                raise wlrepo.OutdatedException("You must update your document before share.")

            # now check if there is anything to do
            need_work, info = self.would_share()
            
            if not need_work:
                return self.shared()          
      
            # The good situation
            #
            #         * local
            #         |
            #        >* 
            #        ||
            #       / |
            # main *  *
            #      |  |
            shared = self.shared()

            try:
                success = shared._revision.merge_with(self._revision, user=self.owner, message=message)
                if not success:
                    raise wlrepo.LibraryException("Merge failed.")
                
                return shared.latest()
            except Abort, e:
                raise wlrepo.LibraryException( repr(e) )
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

