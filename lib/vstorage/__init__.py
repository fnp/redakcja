# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import tempfile
import datetime
import mimetypes
import urllib
import functools

import logging
logger = logging.getLogger('fnp.hazlenut.vstorage')

# Note: we have to set these before importing Mercurial
os.environ['HGENCODING'] = 'utf-8'
os.environ['HGMERGE'] = "internal:merge"

import mercurial.hg
import mercurial.revlog
import mercurial.util

from vstorage.hgui import SilentUI


def urlquote(url, safe='/'):
    """Quotes URL

    >>> urlquote(u'Za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144')
    'Za%C5%BC%C3%B3%C5%82%C4%87%20g%C4%99%C5%9Bl%C4%85%20ja%C5%BA%C5%84'
    """
    return urllib.quote(url.encode('utf-8', 'ignore'), safe)


def urlunquote(url):
    """Unqotes URL

    # >>> urlunquote('Za%C5%BC%C3%B3%C5%82%C4%87_g%C4%99%C5%9Bl%C4%85_ja%C5%BA%C5%84')
    # u'Za\u017c\xf3\u0142\u0107_g\u0119\u015bl\u0105 ja\u017a\u0144'
    """
    return unicode(urllib.unquote(url), 'utf-8', 'ignore')


def find_repo_path(path):
    """Go up the directory tree looking for a Mercurial repository (a directory containing a .hg subdirectory)."""
    while not os.path.isdir(os.path.join(path, ".hg")):
        old_path, path = path, os.path.dirname(path)
        if path == old_path:
            return None
    return path


def with_working_copy_locked(func):
    """A decorator for locking the repository when calling a method."""

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrap the original function in locks."""
        wlock = self.repo.wlock()
        try:
            return func(self, *args, **kwargs)
        finally:
            wlock.release()
    return wrapped


def with_storage_locked(func):
    """A decorator for locking the repository when calling a method."""

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrap the original function in locks."""
        lock = self.repo.lock()
        try:
            return func(self, *args, **kwargs)
        finally:
            lock.release()
    return wrapped


def guess_mime(file_name):
    """
    Guess file's mime type based on extension.
    Default of text/x-wiki for files without an extension.

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

        self.ui = SilentUI()

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

    def _file_path(self, title, type='.xml'):
        return os.path.join(self.path, urlquote(title, safe='')) + type

    def _title_to_file(self, title, type=".xml"):
        return os.path.join(self.repo_prefix, urlquote(title, safe='')) + type

    def _file_to_title(self, filename):
        assert filename.startswith(self.repo_prefix)
        name = filename[len(self.repo_prefix):].strip('/').split('.', 1)[0]
        return urlunquote(name)

    def __contains__(self, title):
        return self._title_to_file(title) in self.repo['tip']

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

    @with_working_copy_locked
    @with_storage_locked
    def save_file(self, title, file_name, **kwargs):
        """Save an existing file as specified page."""

        author = kwargs.get('author', u'anonymous').encode('utf-8')
        comment = kwargs.get('comment', u'Empty comment.').encode('utf-8')
        parent = kwargs.get('parent', None)

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
            msg = self.merge_changes(changectx, repo_file, comment, author, parent)
            author = '<wiki>'
            comment = msg.encode('utf-8')

        logger.debug("Commiting %r", repo_file)

        self._commit([repo_file], comment, author)

    def save_data(self, title, data, **kwargs):
        """Save data as specified page."""
        try:
            temp_path = tempfile.mkdtemp(dir=self.path)
            file_path = os.path.join(temp_path, 'saved')
            f = open(file_path, "wb")
            f.write(data)
            f.close()

            return self.save_file(title=title, file_name=file_path, **kwargs)
        finally:
            try:
                os.unlink(file_path)
            except OSError:
                pass
            try:
                os.rmdir(temp_path)
            except OSError:
                pass

    def save_text(self, **kwargs):
        """Save text as specified page, encoded to charset."""
        text = kwargs.pop('text')
        return self.save_data(data=text.encode(self.charset), **kwargs)

    def _commit(self, files, comment, user):
        match = mercurial.match.exact(self.repo_path, '', list(files))
        return self.repo.commit(match=match, text=comment, user=user, force=True)

    @with_working_copy_locked
    @with_storage_locked
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

    def page_text(self, title, revision=None):
        """Read unicode text of a page."""
        ctx = self._find_filectx(title, revision)

        if ctx is None:
            raise DocumentNotFound(title)

        return ctx.data().decode(self.charset, 'replace'), ctx.filerev()

    def page_text_by_tag(self, title, tag):
        """Read unicode text of a taged page."""
        fname = self._title_to_file(title)
        tag = u"{fname}#{tag}".format(**locals()).encode('utf-8')

        try:
            ctx = self.repo[tag][fname]
            return ctx.data().decode(self.charset, 'replace'), ctx.filerev()
        except IndexError:
            raise DocumentNotFound(fname)

    @with_working_copy_locked
    def page_file_meta(self, title):
        """Get page's inode number, size and last modification time."""
        try:
            (_st_mode, st_ino, _st_dev, _st_nlink, _st_uid, _st_gid, st_size,
             _st_atime, st_mtime, _st_ctime) = os.stat(self._file_path(title))
        except OSError:
            return 0, 0, 0
        return st_ino, st_size, st_mtime

    @with_working_copy_locked
    def page_meta(self, title, revision=None):
        """Get page's revision, date, last editor and his edit comment."""
        fctx = self._find_filectx(title, revision)

        if fctx is None:
            raise DocumentNotFound(title)

        return {
            "revision": fctx.filerev(),
            "date": datetime.datetime.fromtimestamp(fctx.date()[0]),
            "author": fctx.user().decode("utf-8", 'replace'),
            "comment": fctx.description().decode("utf-8", 'replace'),
        }

    def repo_revision(self):
        return self.repo['tip'].rev()

    def _changectx(self):
        return self.repo['tip']

    def page_mime(self, title):
        """
        Guess page's mime type based on corresponding file name.
        Default ot text/x-wiki for files without an extension.
        """
        return guess_mime(self._file_path(title))

    def _find_filectx(self, title, rev=None):
        """Find the last revision in which the file existed."""
        tip = self._changectx()  # start with tip

        def tree_search(tip, repo_file):
            logging.info("Searching for %r", repo_file)
            current = tip
            visited = set()

            stack = [current]
            visited.add(current)

            while repo_file not in current:
                if not stack:
                    raise LookupError

                current = stack.pop()
                for parent in current.parents():
                    if parent not in visited:
                        stack.append(parent)
                        visited.add(parent)

            fctx = current[repo_file]
            if rev is not None:
                fctx = fctx.filectx(rev)
                fctx.filerev()
            return fctx

        try:
            return tree_search(tip, self._title_to_file(title))
        except (IndexError, LookupError):
            logging.info("XML file not found, trying plain")
            try:
                return tree_search(tip, self._title_to_file(title, type=''))
            except (IndexError, LookupError):
                raise DocumentNotFound(title)

    def page_history(self, title):
        """Iterate over the page's history."""

        filectx_tip = self._find_filectx(title)

        maxrev = filectx_tip.filerev()
        minrev = 0
        for rev in range(maxrev, minrev - 1, -1):
            filectx = filectx_tip.filectx(rev)
            date = datetime.datetime.fromtimestamp(filectx.date()[0])
            author = filectx.user().decode('utf-8', 'replace')
            comment = filectx.description().decode("utf-8", 'replace')
            tags = [t.rsplit('#', 1)[-1] for t in filectx.changectx().tags() if '#' in t]

            yield {
                "version": rev,
                "date": date,
                "author": author,
                "description": comment,
                "tag": tags,
            }

    @with_working_copy_locked
    def add_page_tag(self, title, rev, tag, user, doctag=True):
        ctitle = self._title_to_file(title)

        if doctag:
            tag = u"{ctitle}#{tag}".format(**locals()).encode('utf-8')

        message = u"Assigned tag {tag!r} to version {rev!r} of {ctitle!r}".format(**locals()).encode('utf-8')

        fctx = self._find_filectx(title, rev)
        self.repo.tag(
            names=tag, node=fctx.node(), local=False,
            user=user, message=message, date=None,
        )

    def history(self):
        """Iterate over the history of entire wiki."""

        changectx = self._changectx()
        maxrev = changectx.rev()
        minrev = 0
        for wiki_rev in range(maxrev, minrev - 1, -1):
            change = self.repo.changectx(wiki_rev)
            date = datetime.datetime.fromtimestamp(change.date()[0])
            author = change.user().decode('utf-8', 'replace')
            comment = change.description().decode("utf-8", 'replace')
            for repo_file in change.files():
                if repo_file.startswith(self.repo_prefix):
                    title = self._file_to_title(repo_file)
                    try:
                        rev = change[repo_file].filerev()
                    except mercurial.revlog.LookupError:
                        rev = -1
                    yield title, rev, date, author, comment

    def all_pages(self, type=''):
        tip = self.repo['tip']
        """Iterate over the titles of all pages in the wiki."""
        return [self._file_to_title(filename) for filename in tip
                  if not filename.startswith('.')
                    and filename.endswith(type) ]

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
        for filename in modified + added + removed + deleted:
            if filename.startswith(self.repo_prefix):
                yield self._file_to_title(filename)

    def revert(self, pageid, rev, **commit_args):
        """ Make the given version of page the current version (reverting changes). """

        # Find the old version
        fctx = self._find_filectx(pageid, rev)

        # Restore the contents
        self.save_data(pageid, fctx.data(), **commit_args)
