## -*- encoding: utf-8 -*-
#
#__author__ = "Łukasz Rekucki"
#__date__ = "$2009-09-18 10:49:24$"
#
#__doc__ = """RAL implementation over Mercurial"""
#
#import mercurial
#from mercurial import localrepo as hglrepo
#from mercurial import ui as hgui
#from mercurial.node import nullid
#import re
#import wlrepo
#
#FILTER = re.compile(r"^pub_(.+)\.xml$", re.UNICODE)
#
#def default_filter(name):
#    m = FILTER.match(name)
#    if m is not None:
#        return name, m.group(1)
#    return None
#
#class MercurialLibrary(wlrepo.Library):
#
#    def __init__(self, path, maincabinet="default", ** kwargs):
#        super(wlrepo.Library, self).__init__( ** kwargs)
#
#        self._hgui = hgui.ui()
#        self._hgui.config('ui', 'quiet', 'true')
#        self._hgui.config('ui', 'interactive', 'false')
#
#        import os.path
#        self._ospath = self._sanitize_string(os.path.realpath(path))
#
#        maincabinet = self._sanitize_string(maincabinet)
#
#        if os.path.isdir(path):
#            try:
#                self._hgrepo = hglrepo.localrepository(self._hgui, path)
#            except mercurial.error.RepoError:
#                raise wlrepo.LibraryException("[HGLibrary] Not a valid repository at path '%s'." % path)
#        elif kwargs.get('create', False):
#            os.makedirs(path)
#            try:
#                self._hgrepo = hglrepo.localrepository(self._hgui, path, create=1)
#            except mercurial.error.RepoError:
#                raise wlrepo.LibraryException("[HGLibrary] Can't create a repository on path '%s'." % path)
#        else:
#            raise wlrepo.LibraryException("[HGLibrary] Can't open a library on path '%s'." % path)
#
#        # fetch the main cabinet
#        lock = self._hgrepo.lock()
#        try:
#            btags = self._hgrepo.branchtags()
#
#            if not self._has_branch(maincabinet):
#                raise wlrepo.LibraryException("[HGLibrary] No branch named '%s' to init main cabinet" % maincabinet)
#
#            self._maincab = MercurialCabinet(self, maincabinet)
#        finally:
#            lock.release()
#
#    @property
#    def ospath(self):
#        return self._ospath
#
#    @property
#    def main_cabinet(self):
#        return self._maincab
#
#    def document(self, docid, user, part=None, shelve=None):
#        return self.cabinet(docid, user, create=False).retrieve(part=part, shelve=shelve)
#
#    def cabinet(self, docid, user, create=False):
#        docid = self._sanitize_string(docid)
#        user = self._sanitize_string(user)
#
#        bname = self._bname(user, docid)
#
#        lock = self._lock(True)
#        try:
#            if self._has_branch(bname):
#                return MercurialCabinet(self, doc=docid, user=user)
#
#            if not create:
#                raise wlrepo.CabinetNotFound(bname)
#
#            # check if the docid exists in the main cabinet
#            needs_touch = not self._maincab.exists(docid)
#            cab = MercurialCabinet(self, doc=docid, user=user)
#
#            name, fileid = cab._filename(None)
#
#            def cleanup_action(l):
#                if needs_touch:
#                    l._fileopener()(fileid, "w").write('')
#                    l._fileadd(fileid)
#
#                garbage = [fid for (fid, did) in l._filelist() if not did.startswith(docid)]
#                l._filesrm(garbage)
#                print "removed: ", garbage
#
#            # create the branch
#            self._create_branch(bname, before_commit=cleanup_action)
#            return MercurialCabinet(self, doc=docid, user=user)
#        finally:
#            lock.release()
#
#    #
#    # Private methods
#    #
#
#    #
#    # Locking
#    #
#
#    def _lock(self, write_mode=False):
#        return self._hgrepo.wlock() # no support for read/write mode yet
#
#    def _transaction(self, write_mode, action):
#        lock = self._lock(write_mode)
#        try:
#            return action(self)
#        finally:
#            lock.release()
#
#    #
#    # Basic repo manipulation
#    #
#
#    def _checkout(self, rev, force=True):
#        return MergeStatus(mercurial.merge.update(self._hgrepo, rev, False, force, None))
#
#    def _merge(self, rev):
#        """ Merge the revision into current working directory """
#        return MergeStatus(mercurial.merge.update(self._hgrepo, rev, True, False, None))
#
#    def _common_ancestor(self, revA, revB):
#        return self._hgrepo[revA].ancestor(self.repo[revB])
#
#    def _commit(self, message, user=u"library"):
#        return self._hgrepo.commit(text=message, user=user)
#
#
#    def _fileexists(self, fileid):
#        return (fileid in self._hgrepo[None])
#
#    def _fileadd(self, fileid):
#        return self._hgrepo.add([fileid])
#
#    def _filesadd(self, fileid_list):
#        return self._hgrepo.add(fileid_list)
#
#    def _filerm(self, fileid):
#        return self._hgrepo.remove([fileid])
#
#    def _filesrm(self, fileid_list):
#        return self._hgrepo.remove(fileid_list)
#
#    def _filelist(self, filter=default_filter):
#        for name in  self._hgrepo[None]:
#            result = filter(name)
#            if result is None: continue
#
#            yield result
#
#    def _fileopener(self):
#        return self._hgrepo.wopener
#
#    def _filectx(self, fileid, branchid):
#        return self._hgrepo.filectx(fileid, changeid=branchid)
#
#    def _changectx(self, nodeid):
#        return self._hgrepo.changectx(nodeid)
#
#    #
#    # BASIC BRANCH routines
#    #
#
#    def _bname(self, user, docid):
#        """Returns a branch name for a given document and user."""
#        docid = self._sanitize_string(docid)
#        uname = self._sanitize_string(user)
#        return "personal_" + uname + "_file_" + docid;
#
#    def _has_branch(self, name):
#        return self._hgrepo.branchmap().has_key(self._sanitize_string(name))
#
#    def _branch_tip(self, name):
#        name = self._sanitize_string(name)
#        return self._hgrepo.branchtags()[name]
#
#    def _create_branch(self, name, parent=None, before_commit=None):
#        name = self._sanitize_string(name)
#
#        if self._has_branch(name): return # just exit
#
#        if parent is None:
#            parent = self._maincab
#
#        parentrev = parent._hgtip()
#
#        self._checkout(parentrev)
#        self._hgrepo.dirstate.setbranch(name)
#
#        if before_commit: before_commit(self)
#
#        self._commit("[AUTO] Initial commit for branch '%s'." % name, user='library')
#
#        # revert back to main
#        self._checkout(self._maincab._hgtip())
#        return self._branch_tip(name)
#
#    def _switch_to_branch(self, branchname):
#        current = self._hgrepo[None].branch()
#
#        if current == branchname:
#            return current # quick exit
#
#        self._checkout(self._branch_tip(branchname))
#        return branchname
#
#    def shelf(self, nodeid=None):
#        if nodeid is None:
#            nodeid = self._maincab._name
#        return MercurialShelf(self, self._changectx(nodeid))
#
#
#    #
#    # Utils
#    #
#
#    @staticmethod
#    def _sanitize_string(s):
#        if isinstance(s, unicode):
#            s = s.encode('utf-8')
#        return s
#
#class MercurialCabinet(wlrepo.Cabinet):
#
#    def __init__(self, library, branchname=None, doc=None, user=None):
#        if doc and user:
#            super(MercurialCabinet, self).__init__(library, doc=doc, user=user)
#            self._branchname = library._bname(user=user, docid=doc)
#        elif branchname:
#            super(MercurialCabinet, self).__init__(library, name=branchname)
#            self._branchname = branchname
#        else:
#            raise ValueError("Provide either doc/user or branchname")
#
#    def shelf(self):
#        return self._library.shelf(self._branchname)
#
#    def parts(self):
#        return self._execute_in_branch(action=lambda l, c: (e[1] for e in l._filelist()))
#
#    def retrieve(self, part=None, shelf=None):
#        name, fileid = self._filename(part)
#
#        print "Retrieving document %s from cab %s" % (name, self._name)
#
#        if fileid is None:
#            raise wlrepo.LibraryException("Can't retrieve main document from main cabinet.")
#
#        def retrieve_action(l,c):
#            if l._fileexists(fileid):
#                return MercurialDocument(c, name=name, fileid=fileid)
#            print "File %s not found " % fileid
#            return None
#
#        return self._execute_in_branch(retrieve_action)
#
#    def create(self, name, initial_data):
#        name, fileid = self._filename(name)
#
#        if name is None:
#            raise ValueError("Can't create main doc for maincabinet.")
#
#        def create_action(l, c):
#            if l._fileexists(fileid):
#                raise wlrepo.LibraryException("Can't create document '%s' in cabinet '%s' - it already exists" % (fileid, c.name))
#
#            fd = l._fileopener()(fileid, "w")
#            fd.write(initial_data)
#            fd.close()
#            l._fileadd(fileid)
#            l._commit("File '%s' created." % fileid)
#            return MercurialDocument(c, fileid=fileid, name=name)
#
#        return self._execute_in_branch(create_action)
#
#    def exists(self, part=None, shelf=None):
#        name, filepath = self._filename(part)
#
#        if filepath is None: return False
#        return self._execute_in_branch(lambda l, c: l._fileexists(filepath))
#
#    def _execute_in_branch(self, action, write=False):
#        def switch_action(library):
#            old = library._switch_to_branch(self._branchname)
#            try:
#                return action(library, self)
#            finally:
#                library._switch_to_branch(old)
#
#        return self._library._transaction(write_mode=write, action=switch_action)
#
#
#    def _filename(self, docid):
#        return self._partname(docid, 'xml')
#
#    def _partname(self, docid, part):
#        docid = self._library._sanitize_string(part)
#        part = self._library._sanitize_string(part)
#
#        if part is None:
#            part = 'xml'
#
#        if self._maindoc == '' and docid is None:
#            return None
#
#        return 'pub_' + docid + '.' + part
#
#    def _fileopener(self):
#        return self._library._fileopener()
#
#    def _hgtip(self):
#        return self._library._branch_tip(self._branchname)
#
#    def _filectx(self, fileid):
#        return self._library._filectx(fileid, self._branchname)
#
#    def ismain(self):
#        return (self._library.main_cabinet == self)
#
#class MercurialDocument(wlrepo.Document):
#
#    def __init__(self, cabinet, docid):
#        super(MercurialDocument, self).__init__(cabinet, name=docid)
#        self._opener = self._cabinet._fileopener()
#        self._docid = docid
#        self._ctxs = {}
#
#    def _ctx(self, part):
#        if not self._ctxs.has_key(part):
#            self._ctxs[part] = self._cabinet._filectx(self._fileid())
#        return self._ctxs[part]
#
#    def _fileid(self, part='xml'):
#        return self._cabinet._partname(self._docid, part)
#
#    def read(self, part='xml'):
#        return self._opener(self._ctx(part).path(), "r").read()
#
#    def write(self, data, part='xml'):
#        return self._opener(self._ctx(part).path(), "w").write(data)
#
#    def commit(self, message, user):
#        """Commit all parts of the document."""
#        self.library._fileadd(self._fileid)
#        self.library._commit(self._fileid, message, user)
#
#    def update(self):
#        """Update parts of the document."""
#        lock = self.library._lock()
#        try:
#            if self._cabinet.ismain():
#                return True # always up-to-date
#
#            user = self._cabinet.username or 'library'
#            mdoc = self.library.document(self._fileid)
#
#            mshelf = mdoc.shelf()
#            shelf = self.shelf()
#
#            if not mshelf.ancestorof(shelf) and not shelf.parentof(mshelf):
#                shelf.merge_with(mshelf, user=user)
#
#            return True
#        finally:
#            lock.release()
#
#    def share(self, message):
#        lock = self.library._lock()
#        try:
#            print "sharing from", self._cabinet, self._cabinet.username
#
#            if self._cabinet.ismain():
#                return True # always shared
#
#            if self._cabinet.username is None:
#                raise ValueError("Can only share documents from personal cabinets.")
#
#            user = self._cabinet.username
#
#            main = self.library.shelf()
#            local = self.shelf()
#
#            no_changes = True
#
#            # Case 1:
#            #         * local
#            #         |
#            #         * <- can also be here!
#            #        /|
#            #       / |
#            # main *  *
#            #      |  |
#            # The local branch has been recently updated,
#            # so we don't need to update yet again, but we need to
#            # merge down to default branch, even if there was
#            # no commit's since last update
#
#            if main.ancestorof(local):
#                print "case 1"
#                main.merge_with(local, user=user, message=message)
#                no_changes = False
#            # Case 2:
#            #
#            # main *  * local
#            #      |\ |
#            #      | \|
#            #      |  *
#            #      |  |
#            #
#            # Default has no changes, to update from this branch
#            # since the last merge of local to default.
#            elif local.has_common_ancestor(main):
#                print "case 2"
#                if not local.parentof(main):
#                    main.merge_with(local, user=user, message=message)
#                    no_changes = False
#
#            # Case 3:
#            # main *
#            #      |
#            #      * <- this case overlaps with previos one
#            #      |\
#            #      | \
#            #      |  * local
#            #      |  |
#            #
#            # There was a recent merge to the defaul branch and
#            # no changes to local branch recently.
#            #
#            # Use the fact, that user is prepared to see changes, to
#            # update his branch if there are any
#            elif local.ancestorof(main):
#                print "case 3"
#                if not local.parentof(main):
#                    local.merge_with(main, user=user, message='Local branch update.')
#                    no_changes = False
#            else:
#                print "case 4"
#                local.merge_with(main, user=user, message='Local branch update.')
#                local = self.shelf()
#                main.merge_with(local, user=user, message=message)
#
#            print "no_changes: ", no_changes
#            return no_changes
#        finally:
#            lock.release()
#
#    def shared(self):
#        return self.library.main_cabinet.retrieve(self._name)
#
#    def exists(self, part='xml'):
#        return self._cabinet.exists(self._fileid(part))
#
#    @property
#    def size(self):
#        return self._filectx.size()
#
#    def shelf(self):
#        return self._cabinet.shelf()
#
#    @property
#    def last_modified(self):
#        return self._filectx.date()
#
#    def __str__(self):
#        return u"Document(%s->%s)" % (self._cabinet.name, self._name)
#
#    def __eq__(self, other):
#        return self._filectx == other._filectx
#
#
#
#class MercurialShelf(wlrepo.Shelf):
#
#    def __init__(self, lib, changectx):
#        super(MercurialShelf, self).__init__(lib)
#
#        if isinstance(changectx, str):
#            self._changectx = lib._changectx(changectx)
#        else:
#            self._changectx = changectx
#
#    @property
#    def _rev(self):
#        return self._changectx.node()
#
#    def __str__(self):
#        return self._changectx.hex()
#
#    def __repr__(self):
#        return "MercurialShelf(%s)" % self._changectx.hex()
#
#    def ancestorof(self, other):
#        nodes = list(other._changectx._parents)
#        while nodes[0].node() != nullid:
#            v = nodes.pop(0)
#            if v == self._changectx:
#                return True
#            nodes.extend( v._parents )
#        return False
#
#    def parentof(self, other):
#        return self._changectx in other._changectx._parents
#
#    def has_common_ancestor(self, other):
#        a = self._changectx.ancestor(other._changectx)
#        # print a, self._changectx.branch(), a.branch()
#
#        return (a.branch() == self._changectx.branch())
#
#    def merge_with(self, other, user, message):
#        lock = self._library._lock(True)
#        try:
#            self._library._checkout(self._changectx.node())
#            self._library._merge(other._changectx.node())
#            self._library._commit(user=user, message=message)
#        finally:
#            lock.release()
#
#    def __eq__(self, other):
#        return self._changectx.node() == other._changectx.node()
#
#
#class MergeStatus(object):
#    def __init__(self, mstatus):
#        self.updated = mstatus[0]
#        self.merged = mstatus[1]
#        self.removed = mstatus[2]
#        self.unresolved = mstatus[3]
#
#    def isclean(self):
#        return self.unresolved == 0
#
#class UpdateStatus(object):
#
#    def __init__(self, mstatus):
#        self.modified = mstatus[0]
#        self.added = mstatus[1]
#        self.removed = mstatus[2]
#        self.deleted = mstatus[3]
#        self.untracked = mstatus[4]
#        self.ignored = mstatus[5]
#        self.clean = mstatus[6]
#
#    def has_changes(self):
#        return bool(len(self.modified) + len(self.added) + \
#                    len(self.removed) + len(self.deleted))
#
#__all__ = ["MercurialLibrary"]