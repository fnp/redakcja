# -*- coding: utf-8 -*-
import filecmp
import json
import re
from datetime import date
from functools import wraps
from inspect import getargspec
from os import listdir
from os.path import join
from shutil import move, rmtree

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string


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


class AjaxError(Exception):
    pass


def ajax(method, template=None, login_required=False, permission_required=None):
    def decorator(fun):
        @wraps(fun)
        def ajax_view(request):
            kwargs = {}
            request_params = None
            if method == 'post':
                request_params = request.POST
            elif method == 'get':
                request_params = request.GET
            fun_params, xx, fun_kwargs, defaults = getargspec(fun)
            if defaults:
                required_params = fun_params[1:-len(defaults)]
            else:
                required_params = fun_params[1:]
            missing_params = set(required_params) - set(request_params)
            if missing_params:
                res = {
                    'result': 'error',
                    'msg': 'missing params: %s' % ', '.join(missing_params),
                }
            else:
                if request_params:
                    request_params = dict(
                        (key, json.loads(value))
                        for key, value in request_params.iteritems()
                        if fun_kwargs or key in fun_params)
                    kwargs.update(request_params)
                res = None
                if login_required and not request.user.is_authenticated():
                    res = {'result': 'error', 'msg': 'logout'}
                if (permission_required and
                        not request.user.has_perm(permission_required)):
                    res = {'result': 'error', 'msg': 'access denied'}
            if not res:
                try:
                    res = fun(request, **kwargs)
                    if res and template:
                        res = {'html': render_to_string(template, res, RequestContext(request))}
                except AjaxError as e:
                    res = {'result': e.args[0]}
            if 'result' not in res:
                res['result'] = 'ok'
            return HttpResponse(json.dumps(res), content_type='application/json; charset=utf-8')

        return ajax_view

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
        """Check if we have gallery size recorded"""
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
            print "compare %s with %s" % (files[-1], files_other[0])
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
                if p > last_pfx:
                    last_pfx = p
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
                if pfx not in prefixes:
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
            move(join(self.path(self.dest), frm), join(self.path(self.dest), to))
        for frm, to in renamed_files_other.items():
            move(join(self.path(self.src), frm), join(self.path(self.dest), to))

        rmtree(join(self.path(self.src)))
        return self.dest
