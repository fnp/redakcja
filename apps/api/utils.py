# -*- encoding: utf-8 -*-

__author__ = "Łukasz Rekucki"
__date__ = "$2009-09-20 21:48:03$"
__doc__ = "Module documentation."


from functools import wraps
from piston.emitters import Emitter
from piston.utils import rc

import api.response

import wlrepo
import settings

class TextEmitter(Emitter):
    def render(self, request):
        return unicode(self.construct())

Emitter.register('raw', TextEmitter, 'text/plain; charset=utf-8')
Emitter.register('rawhtml', TextEmitter, 'text/html; charset=utf-8')
Emitter.register('rawxml', TextEmitter, 'application/xml; charset=utf-8')

class DjangoAuth(object):

    def is_authenticated(self, request):
        return request.user.is_authenticated()

    def challenge(self):
        return rc.FORBIDDEN


def validate_form(formclass, source='GET'):
  
    def decorator(func):
        @wraps(func)
        def decorated(self, request, * args, ** kwargs):
            form = formclass(getattr(request, source), request.FILES)

            if not form.is_valid():
                errorlist = [{'field': k, 'errors': str(e)} for k, e in form.errors.items()]
                return api.response.BadRequest().django_response(errorlist)

            kwargs['form'] = form
            return func(self, request, * args, ** kwargs)
        return decorated
    return decorator
    
def hglibrary(func):
    @wraps(func)
    def decorated(self, *args, **kwargs):
        l = wlrepo.open_library(settings.REPOSITORY_PATH, 'hg')
        kwargs['lib'] = l
        return func(self, *args, **kwargs)
    return decorated



import re
NAT_EXPR = re.compile(r'(\d+)', re.LOCALE | re.UNICODE)
def natural_order(get_key=lambda x: x):
    def getter(key):
        key = [int(x) if n%2 else x for (n,x) in enumerate(NAT_EXPR.split(get_key(key))) ]
        return key

    return getter

