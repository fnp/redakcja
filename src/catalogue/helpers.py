# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date
from functools import wraps
from os.path import join
from os import listdir, stat
from shutil import move, rmtree
from django.conf import settings
import re
import filecmp

from django.db.models import Count


def active_tab(tab):
    """
        View decorator, which puts tab info on a request.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(request, *args, **kwargs):
            request.catalogue_active_tab = tab
            return f(request, *args, **kwargs)
        return wrapped
    return wrapper


def cached_in_field(field_name):
    def decorator(f):
        @property
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            value = getattr(self, field_name)
            if value is None:
                value = f(self, *args, **kwargs)
                type(self)._default_manager.filter(pk=self.pk).update(**{field_name: value})
            return value
        return wrapped
    return decorator


def parse_isodate(isodate):
    try:
        return date(*[int(p) for p in isodate.split('-')])
    except (AttributeError, TypeError, ValueError):
        raise ValueError("Not a date in ISO format.")


class GalleryMerger(object):
    def __init__(self, dest_gallery, src_gallery):
        self.dest = dest_gallery
        self.src = src_gallery
        self.dest_size = None
        self.src_size = None
        self.num_deleted = 0

    @staticmethod
    def path(gallery):
        return join(settings.MEDIA_ROOT, settings.IMAGE_DIR, gallery)

    @staticmethod
    def get_prefix(name):
        m = re.match(r"^([0-9])-", name)
        if m:
            return int(m.groups()[0])
        return None

    @staticmethod
    def set_prefix(name, prefix, always=False):
        m = not always and re.match(r"^([0-9])-", name)
        return "%1d-%s" % (prefix, m and name[2:] or name)

    @property
    def was_merged(self):
        "Check if we have gallery size recorded"
        return self.dest_size is not None

    def merge(self):
        if not self.dest:
            return self.src
        if not self.src:
            return self.dest

        files = listdir(self.path(self.dest))
        files.sort()
        self.dest_size = len(files)
        files_other = listdir(self.path(self.src))
        files_other.sort()
        self.src_size = len(files_other)

        if files and files_other:
            if filecmp.cmp(
                    join(self.path(self.dest), files[-1]),
                    join(self.path(self.src), files_other[0]),
                    False
                    ):
                files_other.pop(0)
                self.num_deleted = 1

        prefixes = {}
        renamed_files = {}
        renamed_files_other = {}
        last_pfx = -1

        # check if all elements of my files have a prefix
        files_prefixed = True
        for f in files:
            p = self.get_prefix(f)
            if p:
                if p > last_pfx: last_pfx = p
            else:
                files_prefixed = False
                break

        # if not, add a 0 prefix to them
        if not files_prefixed:
            prefixes[0] = 0
            for f in files:
                renamed_files[f] = self.set_prefix(f, 0, True)

        # two cases here - either all are prefixed or not.
        files_other_prefixed = True
        for f in files_other:
            pfx = self.get_prefix(f)
            if pfx is not None:
                if not pfx in prefixes:
                    last_pfx += 1
                    prefixes[pfx] = last_pfx
                renamed_files_other[f] = self.set_prefix(f, prefixes[pfx])
            else:
                # ops, not all files here were prefixed.
                files_other_prefixed = False
                break

        # just set a 1- prefix to all of them
        if not files_other_prefixed:
            for f in files_other:
                renamed_files_other[f] = self.set_prefix(f, 1, True)

        # finally, move / rename files.
        for frm, to in renamed_files.items():
            move(join(self.path(self.dest), frm),
                        join(self.path(self.dest), to))
        for frm, to in renamed_files_other.items():
            move(join(self.path(self.src), frm),
                        join(self.path(self.dest), to))            

        rmtree(join(self.path(self.src)))
        return self.dest
