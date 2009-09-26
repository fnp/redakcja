# -*- encoding: utf-8 -*-

__author__ = "Łukasz Rekucki"
__date__ = "$2009-09-20 21:48:03$"
__doc__ = "Module documentation."


from functools import wraps
from piston.emitters import Emitter
from piston.utils import rc

import api.response

from wlrepo import MercurialLibrary
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
        l = MercurialLibrary(settings.REPOSITORY_PATH)
        kwargs['lib'] = l
        return func(self, *args, **kwargs)
    return decorated
    
            
        

