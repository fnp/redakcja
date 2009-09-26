# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler

from explorer.models import PullRequest

class PullRequestListHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        if request.user.has_perm('explorer.book.can_share'):
            return PullRequest.objects.all()
        else:
            return PullRequest.objects.filter(commiter=request.user)


class PullRequestHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, prq_id):
        return PullRequest.objects.get(id=prq_id)    