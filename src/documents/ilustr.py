# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""Replacing relative addresses of illustrations with absolute URLs."""
import os.path
import re
from urllib.parse import quote, unquote, urljoin
from django.conf import settings


SRC_RE = re.compile(r'''(<ilustr\b[^>]*?\bsrc\s*=\s*)(["'])(.*?)\2''', re.S)


def is_absolute(src):
    return src.startswith(('http://', 'https://'))


def absolutize(text, gallery_url, gallery_dir):
    """Replaces relative `src` of illustrations in text with absolute URLs.

    Only replaces addresses of files which exist in the gallery.
    Returns the new text, a list of replaced and a list of unresolved addresses.
    """
    fixed = []
    unresolved = []

    def repl(m):
        src = m.group(3)
        if is_absolute(src):
            return m.group(0)
        path = os.path.normpath(os.path.join(gallery_dir, unquote(src)))
        if not src or not os.path.isfile(path):
            unresolved.append(src)
            return m.group(0)
        fixed.append(src)
        url = urljoin(gallery_url, quote(src, safe='/%'))
        return m.group(1) + m.group(2) + url + m.group(2)

    return SRC_RE.sub(repl, text), fixed, unresolved


class IlustrFixer:
    def __init__(self, base_url, **author):
        self.images_url = urljoin(base_url, settings.MEDIA_URL + settings.IMAGE_DIR)
        self.images_dir = os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR)
        self.author = author
        self.stats = dict.fromkeys(['books', 'fixed', 'unresolved', 'conflicts'], 0)

    def fix_book(self, book):
        if not book.gallery:
            gallery_url = gallery_dir = None
        else:
            gallery_url = urljoin(self.images_url, quote(book.gallery) + '/')
            gallery_dir = os.path.join(self.images_dir, book.gallery)

        for chunk in book.chunk_set.all():
            head = chunk.head
            if head is None:
                continue
            head_text = head.materialize()
            if gallery_url is None:
                unresolved = [m.group(3) for m in SRC_RE.finditer(head_text)
                              if not is_absolute(m.group(3))]
                if unresolved:
                    self.stats['unresolved'] += len(unresolved)
                continue

            new_text, fixed, unresolved = absolutize(head_text, gallery_url, gallery_dir)
            self.stats['fixed'] += len(fixed)
            self.stats['unresolved'] += len(unresolved)

            if fixed:
                chunk.commit(
                    new_text, description='Pełne adresy ilustracji.',
                    publishable=head.publishable,
                    **self.author)
