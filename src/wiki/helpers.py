from datetime import datetime
from functools import wraps

from django import http
import json
from django.utils.functional import Promise


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
        # get rid of content_type
        kwargs.pop('content_type', None)

        data = json.dumps(data, cls=ExtendedEncoder)
        super(JSONResponse, self).__init__(data, content_type="application/json", **kwargs)


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
            return http.HttpResponse("Login required.", status=401, content_type="text/plain")
        return view(request, *args, **kwargs)
    return authenticated_view


def ajax_require_permission(permission):
    def decorator(view):
        @wraps(view)
        def authorized_view(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                return http.HttpResponse("Access Forbidden.", status=403, content_type="text/plain")
            return view(request, *args, **kwargs)
        return authorized_view
    return decorator
