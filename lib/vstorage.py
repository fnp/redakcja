# -*- coding: utf-8 -*-
import os
import tempfile
import datetime
import mimetypes
import urllib

# Note: we have to set these before importing Mercurial
os.environ['HGENCODING'] = 'utf-8'
os.environ['HGMERGE'] = "internal:merge"

import mercurial.hg
import mercurial.ui
import mercurial.revlog
import mercurial.util


def urlquote(url, safe='/'):
    """Quotes URL 
    
    >>> urlquote(u'Za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144')
    'Za%C5%BC%C3%B3%C5%82%C4%87_g%C4%99%C5%9Bl%C4%85_ja%C5%BA%C5%84'
    """
    return urllib.quote(url.replace(' ', '_').encode('utf-8', 'ignore'), safe)


def urlunquote(url):
    """Unqotes URL 
    
    # >>> urlunquote('Za%C5%BC%C3%B3%C5%82%C4%87_g%C4%99%C5%9Bl%C4%85_ja%C5%BA%C5%84')
    # u'Za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144'
    """
    return unicode(urllib.unquote(url), 'utf-8', 'ignore').replace('_', ' ')


def find_repo_path(path):
    """Go up the directory tree looking for a Mercurial repository (a directory containing a .hg subdirectory)."""
    while not os.path.isdir(os.path.join(path, ".hg")):
        old_path, path = path, os.path.dirname(path)
        if path == old_path:
            return None
    return path


def locked_repo(func):
    """A decorator for locking the repository when calling a method."""

    def new_func(self, *args, **kwargs):
        """Wrap the original function in locks."""

        wlock = self.repo.wlock()
        lock = self.repo.lock()
        try:
            func(self, *args, **kwargs)
        finally:
            lock.release()
            wlock.release()

    return new_func


def guess_mime(file_name):
    """
    Guess file's mime type based on extension.
    Default ot text/x-wiki for files without an extension.

    >>> guess_mime('something.txt')
    'text/plain'
    >>> guess_mime('SomePage')
    'text/x-wiki'
    >>> guess_mime(u'ąęśUnicodePage')
    'text/x-wiki'
    >>> guess_mime('image.png')
    'image/png'
    >>> guess_mime('style.css')
    'text/css'
    >>> guess_mime('archive.tar.gz')
    'archive/gzip'
    """

    mime, encoding = mimetypes.guess_type(file_name, strict=False)
    if encoding:
        mime = 'archive/%s' % encoding
    if mime is None:
        mime = 'text/x-wiki'
    return mime


class DocumentNotFound(Exception):
    pass


class VersionedStorage(object):
    """
    Provides means of storing text pages and keeping track of their
    change history, using Mercurial repository as the storage method.
    """

    def __init__(self, path, charset=None):
        """
        Takes the path to the directory where the pages are to be kept.
        If the directory doen't exist, it will be created. If it's inside
        a Mercurial repository, that repository will be used, otherwise
        a new repository will be created in it.
        """

        self.charset = charset or 'utf-8'
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.repo_path = find_repo_path(self.path)
        try:
            self.ui = mercurial.ui.ui(report_untrusted=False,
                                      interactive=False, quiet=True)
        except TypeError:
            # Mercurial 1.3 changed the way we setup the ui object.
            self.ui = mercurial.ui.ui()
            self.ui.quiet = True
            self.ui._report_untrusted = False
            self.ui.setconfig('ui', 'interactive', False)
        if self.repo_path is None:
            self.repo_path = self.path
            create = True
        else:
            create = False
        self.repo_prefix = self.path[len(self.repo_path):].strip('/')
        self.repo = mercurial.hg.repository(self.ui, self.repo_path,
                                            create=create)

    def reopen(self):
        """Close and reopen the repo, to make sure we are up to date."""

        self.repo = mercurial.hg.repository(self.ui, self.repo_path)

    def _file_path(self, title):
        return os.path.join(self.path, urlquote(title, safe=''))

    def _title_to_file(self, title):
        return os.path.join(self.repo_prefix, urlquote(title, safe=''))

    def _file_to_title(self, filename):
        assert filename.startswith(self.repo_prefix)
        name = filename[len(self.repo_prefix):].strip('/')
        return urlunquote(name)

    def __contains__(self, title):
        return title in self.all_pages()

    def __iter__(self):
        return self.all_pages()        
        
    def merge_changes(self, changectx, repo_file, text, user, parent):
        """Commits and merges conflicting changes in the repository."""
        tip_node = changectx.node()
        filectx = changectx[repo_file].filectx(parent)
        parent_node = filectx.changectx().node()

        self.repo.dirstate.setparents(parent_node)
        node = self._commit([repo_file], text, user)
        
        partial = lambda filename: repo_file == filename
        
        # If p1 is equal to p2, there is no work to do. Even the dirstate is correct.
        p1, p2 = self.repo[None].parents()[0], self.repo[tip_node]
        if p1 == p2:
            return text
        
        try:
            mercurial.merge.update(self.repo, tip_node, True, False, partial)
            msg = 'merge of edit conflict'
        except mercurial.util.Abort:
            msg = 'failed merge of edit conflict'
        
        self.repo.dirstate.setparents(tip_node, node)
        # Mercurial 1.1 and later need updating the merge state
        try:
            mercurial.merge.mergestate(self.repo).mark(repo_file, "r")
        except (AttributeError, KeyError):
            pass
        return msg

    @locked_repo
    def save_file(self, title, file_name, author=u'', comment=u'', parent=None):
        """Save an existing file as specified page."""

        user = author.encode('utf-8') or u'anon'.encode('utf-8')
        text = comment.encode('utf-8') or u'comment'.encode('utf-8')
        repo_file = self._title_to_file(title)
        file_path = self._file_path(title)
        mercurial.util.rename(file_name, file_path)
        changectx = self._changectx()
        try:
            filectx_tip = changectx[repo_file]
            current_page_rev = filectx_tip.filerev()
        except mercurial.revlog.LookupError:
            self.repo.add([repo_file])
            current_page_rev = -1
        if parent is not None and current_page_rev != parent:
            msg = self.merge_changes(changectx, repo_file, text, user, parent)
            user = '<wiki>'
            text = msg.encode('utf-8')
        self._commit([repo_file], text, user)


    def _commit(self, files, text, user):
        try:
            return self.repo.commit(files=files, text=text, user=user,
                                    force=True, empty_ok=True)
        except TypeError:
            # Mercurial 1.3 doesn't accept empty_ok or files parameter
            match = mercurial.match.exact(self.repo_path, '', list(files))
            return self.repo.commit(match=match, text=text, user=user,
                                    force=True)


    def save_data(self, title, data, author=u'', comment=u'', parent=None):
        """Save data as specified page."""

        try:
            temp_path = tempfile.mkdtemp(dir=self.path)
            file_path = os.path.join(temp_path, 'saved')
            f = open(file_path, "wb")
            f.write(data)
            f.close()
            self.save_file(title, file_path, author, comment, parent)
        finally:
            try:
                os.unlink(file_path)
            except OSError:
                pass
            try:
                os.rmdir(temp_path)
            except OSError:
                pass

    def save_text(self, title, text, author=u'', comment=u'', parent=None):
        """Save text as specified page, encoded to charset."""

        data = text.encode(self.charset)
        self.save_data(title, data, author, comment, parent)

    def page_text(self, title):
        """Read unicode text of a page."""

        data = self.open_page(title).read()
        text = unicode(data, self.charset, 'replace')
        return text

    def page_lines(self, page):
        for data in page:
            yield unicode(data, self.charset, 'replace')

    @locked_repo
    def delete_page(self, title, author=u'', comment=u''):
        user = author.encode('utf-8') or 'anon'
        text = comment.encode('utf-8') or 'deleted'
        repo_file = self._title_to_file(title)
        file_path = self._file_path(title)
        try:
            os.unlink(file_path)
        except OSError:
            pass
        self.repo.remove([repo_file])
        self._commit([repo_file], text, user)

    def open_page(self, title):
        if title not in self:
            print 'whatever', list(self.all_pages())
            raise DocumentNotFound()
        
        try:
            return open(self._file_path(title), "rb")
        except IOError:
            raise DocumentNotFound()

    def page_file_meta(self, title):
        """Get page's inode number, size and last modification time."""

        try:
            (st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size,
             st_atime, st_mtime, st_ctime) = os.stat(self._file_path(title))
        except OSError:
            return 0, 0, 0
        return st_ino, st_size, st_mtime

    def page_meta(self, title):
        """Get page's revision, date, last editor and his edit comment."""

        filectx_tip = self._find_filectx(title)
        if filectx_tip is None:
            raise DocumentNotFound()
            #return -1, None, u'', u''
        rev = filectx_tip.filerev()
        filectx = filectx_tip.filectx(rev)
        date = datetime.datetime.fromtimestamp(filectx.date()[0])
        author = unicode(filectx.user(), "utf-8",
                         'replace').split('<')[0].strip()
        comment = unicode(filectx.description(), "utf-8", 'replace')
        return rev, date, author, comment

    def repo_revision(self):
        return self._changectx().rev()

    def page_mime(self, title):
        """
        Guess page's mime type based on corresponding file name.
        Default ot text/x-wiki for files without an extension.
        """
        return guess_type(self._file_path(title))

    def _changectx(self):
        """Get the changectx of the tip."""
        try:
            # This is for Mercurial 1.0
            return self.repo.changectx()
        except TypeError:
            # Mercurial 1.3 (and possibly earlier) needs an argument
            return self.repo.changectx('tip')

    def _find_filectx(self, title):
        """Find the last revision in which the file existed."""

        repo_file = self._title_to_file(title)
        changectx = self._changectx()
        stack = [changectx]
        while repo_file not in changectx:
            if not stack:
                return None
            changectx = stack.pop()
            for parent in changectx.parents():
                if parent != changectx:
                    stack.append(parent)
        return changectx[repo_file]

    def page_history(self, title):
        """Iterate over the page's history."""

        filectx_tip = self._find_filectx(title)
        if filectx_tip is None:
            return
        maxrev = filectx_tip.filerev()
        minrev = 0
        for rev in range(maxrev, minrev-1, -1):
            filectx = filectx_tip.filectx(rev)
            date = datetime.datetime.fromtimestamp(filectx.date()[0])
            author = unicode(filectx.user(), "utf-8",
                             'replace').split('<')[0].strip()
            comment = unicode(filectx.description(), "utf-8", 'replace')
            yield rev, date, author, comment

    def page_revision(self, title, rev):
        """Get unicode contents of specified revision of the page."""

        filectx_tip = self._find_filectx(title)
        if filectx_tip is None:
            raise DocumentNotFound()
        try:
            data = filectx_tip.filectx(rev).data()
        except IndexError:
            raise DocumentNotFound()
        return data

    def revision_text(self, title, rev):
        data = self.page_revision(title, rev)
        text = unicode(data, self.charset, 'replace')
        return text

    def history(self):
        """Iterate over the history of entire wiki."""

        changectx = self._changectx()
        maxrev = changectx.rev()
        minrev = 0
        for wiki_rev in range(maxrev, minrev-1, -1):
            change = self.repo.changectx(wiki_rev)
            date = datetime.datetime.fromtimestamp(change.date()[0])
            author = unicode(change.user(), "utf-8",
                             'replace').split('<')[0].strip()
            comment = unicode(change.description(), "utf-8", 'replace')
            for repo_file in change.files():
                if repo_file.startswith(self.repo_prefix):
                    title = self._file_to_title(repo_file)
                    try:
                        rev = change[repo_file].filerev()
                    except mercurial.revlog.LookupError:
                        rev = -1
                    yield title, rev, date, author, comment

    def all_pages(self):
        """Iterate over the titles of all pages in the wiki."""
        status = self.repo.status(self.repo[None], None, None, True, True, True)
        clean_files = status[6]
        for filename in clean_files:
            yield urlunquote(filename)

    def changed_since(self, rev):
        """Return all pages that changed since specified repository revision."""

        try:
            last = self.repo.lookup(int(rev))
        except IndexError:
            for page in self.all_pages():
                yield page
                return
        current = self.repo.lookup('tip')
        status = self.repo.status(current, last)
        modified, added, removed, deleted, unknown, ignored, clean = status
        for filename in modified+added+removed+deleted:
            if filename.startswith(self.repo_prefix):
                yield self._file_to_title(filename)
