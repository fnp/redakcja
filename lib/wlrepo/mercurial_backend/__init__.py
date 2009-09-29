# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 09:20:22$"
__doc__ = "Module documentation."

import wlrepo
from mercurial.node import nullid

class MercurialRevision(wlrepo.Revision):

    def __init__(self, lib, changectx):
        super(MercurialRevision, self).__init__(lib)
        self._changectx = changectx
        
        branchname = self._changectx.branch()
        if branchname.startswith("$doc:"):
            self._docname = branchname[5:]
            self._username = None
        elif branchname.startswith("$user:"):
            idx = branchname.find("$doc:")
            if(idx < 0):
                raise ValueError("Revision %s is not a valid document revision." % changectx.hex());
            self._username = branchname[6:idx]
            self._docname = branchname[idx+5:]
        else:
            raise ValueError("Revision %s is not a valid document revision." % changectx.hex());
        
    @property
    def document_name(self):
        return self._docname.decode('utf-8')

    @property
    def user_name(self):
        return self._username.decode('utf-8')

    def hgrev(self):
        return self._changectx.node()
        
    def hgcontext(self):
        return self._changectx

    def hgbranch(self):
        return self._changectx.branch()

    @property
    def timestamp(self):
        return self._changectx.date()[0]

    def __unicode__(self):
        return u"%s" % self._changectx.hex()

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return "%s" % self._changectx.hex()

    def ancestorof(self, other):
        nodes = list(other._changectx._parents)
        while nodes[0].node() != nullid:
            v = nodes.pop(0)
            if v == self._changectx:
                return True
            nodes.extend( v._parents )
        return False

    def parentof(self, other):
        return self._changectx in other._changectx._parents

    def has_common_ancestor(self, other):
        a = self._changectx.ancestor(other._changectx)       
        return (a.branch() == self._changectx.branch())

    def has_children(self):
        return bool( self._library._hgrepo.changelog.children(self.hgrev()) )   

    def merge_with(self, other, user, message):
        lock = self._library.lock(True)
        try:
            self._library._checkout(self._changectx.node())
            status = self._library._merge(other._changectx.node())
            if status.isclean():
                self._library._commit(user=user, message=message)
                return (True, True)
            else:
                return (False, False)
        finally:
            lock.release()

    def __eq__(self, other):
        return self._changectx.node() == other._changectx.node()


from wlrepo.mercurial_backend.library import MercurialLibrary


