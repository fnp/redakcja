# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-20 21:48:03$"
__doc__ = "Module documentation."


from piston.emitters import Emitter
from piston.utils import rc

class TextEmitter(Emitter):
    def render(self, request):
        return unicode(self.construct())

Emitter.register('text', TextEmitter, 'text/plain; charset=utf-8')
Emitter.register('rawxml', TextEmitter, 'application/xml; charset=utf-8')


class DjangoAuth(object):

    def is_authenticated(self, request):
        return request.user.is_authenticated()

    def challenge(self):
        return rc.FORBIDDEN