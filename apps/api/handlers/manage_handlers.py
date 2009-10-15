# -*- encoding: utf-8 -*-

import logging
log = logging.getLogger('platforma.api.manage')

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler

from api.utils import hglibrary
from api.models import PullRequest
from api.response import *
from datetime import datetime

class PullRequestListHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        if request.user.has_perm('api.pullrequest.can_change'):
            return PullRequest.objects.all()
        else:
            return PullRequest.objects.filter(commiter=request.user)


class PullRequestHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self, request, prq_id):
        return PullRequest.objects.get(id=prq_id)

    def update(self, request, prq_id):
        """Change the status of request"""

        if not request.user.has_perm('api.pullrequest.can_change'):
            return AccessDenied().django_response("Insufficient priviliges")
        
        prq = PullRequest.objects.get(id=prq_id)

        if not prq:
            return EntityNotFound().django_response()

        action = request.PUT.get('action', None)

        if action == 'accept':
            return self.accept_merge(request.user, prq)
        elif action == 'reject' and prq.status in ['N', 'R']:
            return self.reject_merge(request.user, prq)
        else:
            return BadRequest().django_response()


    @hglibrary
    def accept_merge(self, user, prq, lib):
        if prq.status not in ['N', 'E']:
            return BadRequest().django_response({
                'reason': 'invalid-state',
                'message': "This pull request is alredy resolved. Can't accept."
            })
            
        src_doc = lib.document( prq.source_revision )

        lock = lib.lock()
        try:
            if not src_doc.up_to_date():
                # This revision is no longer up to date, thus
                # it needs to be updated, before push:
                #
                #  Q: where to put the updated revision ?
                #  A: create a special user branch named prq-#prqid
                prq_doc = src_doc.take("$prq-%d" % prd.id)

                # This could be not the first time we try this,
                # so the prq_doc could already be there
                # and up to date

                success, changed = prq_doc.update(user.username)
                prq.status = 'E'

                if not success:
                    prq.save()
                    # this can happen only if the merge program
                    # is misconfigured - try returning an entity conflict
                    # TODO: put some useful infor here
                    return EntityConflict().django_response()

                if changed:
                    prq_doc = prq_doc.latest()

                prq.source_revision = str(prq_doc.revision)
                src_doc = prq_doc

            # check if there are conflicts
            if prq_doc.has_conflict_marks():
                prq.status = 'E'
                prq.save()
                # Now, the user must resolve the conflict
                return EntityConflict().django_response({
                    "reason": "unresolved-conflicts",
                    "message": "There are conflict in the document. Resolve the conflicts retry accepting."
                })

            # So, we have an up-to-date, non-conflicting document
            changed = src_doc.share(prq.comment)

            if not changed:
                # this is actually very bad, but not critical
                log.error("Unsynched pull request: %d" % prq.id)                

            # sync state with repository
            prq.status = 'A'
            prq.merged_revision = str(src_doc.shared().revision)
            prq.merged_timestamp = datetime()
            prq.save()

            return SuccessAllOk().django_response({
                'status': prq.status,
                'merged_into': prq.merged_revision,
                'merged_at': prq.merged_timestamp
            })
        finally:
            lock.release()
    
    def reject_merge(self, prq, lib):
        prq.status = 'R'
        prq.save()

        return SuccessAllOk().django_response({
            'status': prq.status
        })
        

        


        

