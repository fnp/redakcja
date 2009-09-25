# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 09:20:22$"
__doc__ = "Module documentation."

import wlrepo



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
            self._username = branchname[0:idx]
            self._docname = branchname[idx+5:]
        else:
            raise ValueError("Revision %s is not a valid document revision." % changectx.hex());
        
    @property
    def document_name(self):
        return self._docname

    @property
    def user_name(self):
        return self._username

    def hgrev(self):
        return self._changectx.node()
        
    def hgcontext(self):
        return self._changectx

    def hgbranch(self):
        return self._changectx.branch()

    def __unicode__(self):
        return u"%s" % self._changectx.hex()

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

    def merge_with(self, other, user, message):
        lock = self._library._lock(True)
        try:
            self._library._checkout(self._changectx.node())
            self._library._merge(other._changectx.node())
            self._library._commit(user=user, message=message)
        finally:
            lock.release()

    def __eq__(self, other):
        return self._changectx.node() == other._changectx.node()


from wlrepo.mercurial_backend.library import MercurialLibrary


