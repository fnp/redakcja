# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-10-20 12:31:48$"
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
        return self._docname and self._docname.decode('utf-8')

    @property
    def user_name(self):
        return self._username and self._username.decode('utf-8')

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

    def has_children(self, limit_branch=False):
        for child in self._changectx.children():
            cbranch = child.branch()
            if (not limit_branch) or (cbranch == self.hgbranch()):
                return True
        return False

    def has_parent_from(self, rev):
        branch = rev.hgbranch()        
        for parent in self._changectx.parents():
            if parent.branch() == branch:
                return True            
        return False

    def merge_with(self, other, user, message):
        message = self._library._sanitize_string(message)
        lock = self._library.lock(True)
        try:
            self._library._checkout(self._changectx.node())
            status = self._library._merge(other._changectx.node())
            if status.isclean():
                self._library._commit(user=user, message=message)
                return True
            else:
                return False
        finally:
            lock.release()

    def parent(self):
        parents = self._changectx.parents()

        if len(parents) == 1:
            return self._library._revision(parents[0])
        
        if parents[0].branch() == self.hgbranch():
            return self._library._revision(parents[0])
        else:
            return self._library._revision(parents[1]) 
        
    def __eq__(self, other):
        return self._changectx.node() == other._changectx.node()
