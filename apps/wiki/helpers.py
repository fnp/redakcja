from django import http
from django.utils import simplejson as json
from django.utils.functional import Promise
from datetime import datetime
from functools import wraps


class ExtendedEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Promise):
            return unicode(obj)

        if isinstance(obj, datetime):
            return datetime.ctime(obj) + " " + (datetime.tzname(obj) or 'GMT')

        return json.JSONEncoder.default(self, obj)


# shortcut for JSON reponses
class JSONResponse(http.HttpResponse):

    def __init__(self, data={}, **kwargs):
        # get rid of mimetype
        kwargs.pop('mimetype', None)

        data = json.dumps(data, cls=ExtendedEncoder)
        super(JSONResponse, self).__init__(data, mimetype="application/json", **kwargs)


# return errors
class JSONFormInvalid(JSONResponse):
    def __init__(self, form):
        super(JSONFormInvalid, self).__init__(form.errors, status=400)


class JSONServerError(JSONResponse):
    def __init__(self, *args, **kwargs):
        kwargs['status'] = 500
        super(JSONServerError, self).__init__(*args, **kwargs)


def ajax_login_required(view):
    @wraps(view)
    def authenticated_view(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponse("Login required.", status=401, mimetype="text/plain")
        return view(request, *args, **kwargs)
    return authenticated_view


def ajax_require_permission(permission):
    def decorator(view):
        @wraps(view)
        def authorized_view(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                return http.HttpResponse("Access Forbidden.", status=403, mimetype="text/plain")
            return view(request, *args, **kwargs)
        return authorized_view
    return decorator

import collections

def recursive_groupby(iterable):
    """    
#    >>> recursive_groupby([1,2,3,4,5])
#    [1, 2, 3, 4, 5]
    
    >>> recursive_groupby([[1]])
    [1]
    
    >>> recursive_groupby([('a', 1),('a', 2), 3, ('b', 4), 5])
    ['a', [1, 2], 3, 'b', [4], 5]
    
    >>> recursive_groupby([('a', 'x', 1),('a', 'x', 2), ('a', 'x', 3)])
    ['a', ['x', [1, 2, 3]]]
   
    """

    def _generator(iterator):
        group = None
        grouper = None

        for item in iterator:
            if not isinstance(item, collections.Sequence):
                if grouper is not None:
                    yield grouper
                    if len(group):
                        yield recursive_groupby(group)
                    group = None
                    grouper = None
                yield item
                continue
            elif len(item) == 1:
                if grouper is not None:
                    yield grouper
                    if len(group):
                        yield recursive_groupby(group)
                    group = None
                    grouper = None
                yield item[0]
                continue
            elif not len(item):
                continue

            if grouper is None:
                group = [item[1:]]
                grouper = item[0]
                continue

            if grouper != item[0]:
                if grouper is not None:
                    yield grouper
                    if len(group):
                        yield recursive_groupby(group)
                    group = None
                    grouper = None
                group = [item[1:]]
                grouper = item[0]
                continue

            group.append(item[1:])

        if grouper is not None:
            yield grouper
            if len(group):
                yield recursive_groupby(group)
            group = None
            grouper = None

    return list(_generator(iterable))
