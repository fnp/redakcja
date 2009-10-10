# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler

from api.utils import hglibrary
from explorer.models import PullRequest
from api.response import *

class PullRequestListHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        if request.user.has_perm('explorer.book.can_share'):
            return PullRequest.objects.all()
        else:
            return PullRequest.objects.filter(commiter=request.user)


class PullRequestHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self, request, prq_id):
        return PullRequest.objects.get(id=prq_id)

    def update(self, request, prq_id):
        """Change the status of request"""

        if not request.user.has_perm('explorer.document.can_share'):
            return AccessDenied().django_response("Insufficient priviliges")
        
        prq = PullRequest.objects.get(id=prq_id)

        if not prq:
            return EntityNotFound().django_response()


        action = request.PUT.get('action', None)

        if action == 'accept' and prq.status == 'N':
            return self.accept_merge(prq)
        elif action == 'reject' and prq.status in ['N', 'R']:
            return self.reject_merge(prq)
        else:
            return BadRequest().django_response()


    @hglibrary
    def accept_merge(self, prq, lib):        
        doc = lib.document( prq.document )
        udoc = doc.take( prq.comitter.username )
        success, changed = udoc.share(prq.comment)

        if not success:
            return EntityConflict().django_response()

        doc = doc.latest()

        prq.status = 'A'
        prq.merged_revisions = unicode(doc.revision)
        prq.save()
        
        return SuccessAllOk().django_response({
            'status': prq.status
        })

    
    def reject_merge(self, prq, lib):
        prq.status = 'R'
        prq.save()

        return SuccessAllOk().django_response({
            'status': prq.status
        })
        

        


        

