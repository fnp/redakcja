# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-10-19 14:34:42$"
__doc__ = "Module documentation."

#import api.forms as forms
#import api.response as response
#
#from api.utils import validate_form, hglibrary
#from api.models import PartCache
#

#
#from piston.handler import BaseHandler
#
#from wlrepo import *

import re
from library_handlers import *

import librarian
from librarian import parser

#
# Document Text View
#

XINCLUDE_REGEXP = r"""<(?:\w+:)?include\s+[^>]*?href=("|')wlrepo://(?P<link>[^\1]+?)\1\s*[^>]*?>"""
#
#
#

class DocumentTextHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    @validate_form(forms.TextRetrieveForm, 'GET')
    @hglibrary
    def read(self, request, form, docid, lib):
        """Read document as raw text"""
        try:
            revision = form.cleaned_data['revision']
            chunk = form.cleaned_data['chunk']
            user = form.cleaned_data['user'] or request.user.username
            format = form.cleaned_data['format']

            document = lib.document_for_rev(revision)

            if document.id != docid:
                return response.BadRequest().django_response({
                    'reason': 'name-mismatch',
                    'message': 'Provided revision is not valid for this document'
                })

            if document.owner != user:
                return response.BadRequest().django_response({
                    'reason': 'user-mismatch',
                    'message': "Provided revision doesn't belong to user %s" % user
                })

            for error in check_user(request, user):
                return error

            if not chunk:
                return document.data('xml')

            xdoc = parser.WLDocument.from_string(document.data('xml'),\
                parse_dublincore=False)

            xchunk = xdoc.chunk(chunk)

            if xchunk is None:
                return response.EntityNotFound().django_response({
                      'reason': 'no-part-in-document',
                      'path': chunk
                })

            return librarian.serialize_children(xchunk, format=format)

        except librarian.ParseError, e:
            return response.EntityNotFound().django_response({
                'reason': 'invalid-document-state',
                'exception': type(e),
                'message': e.message
            })
        except (EntryNotFound, RevisionNotFound), e:
            return response.EntityNotFound().django_response({
                'reason': 'not-found',
                'exception': type(e), 'message': e.message
            })

    @validate_form(forms.TextUpdateForm, 'POST')
    @hglibrary
    def create(self, request, form, docid, lib):
        try:
            revision = form.cleaned_data['revision']
            msg = form.cleaned_data['message']
            user = form.cleaned_data['user'] or request.user.username

            # do not allow changing not owned documents
            # (for now... )


            if user != request.user.username:
                return response.AccessDenied().django_response({
                    'reason': 'insufficient-priviliges',
                })

            current = lib.document(docid, user)
            orig = lib.document_for_rev(revision)

            if current != orig:
                return response.EntityConflict().django_response({
                        "reason": "out-of-date",
                        "provided_revision": orig.revision,
                        "latest_revision": current.revision })

            if form.cleaned_data.has_key('contents'):
                data = form.cleaned_data['contents']
            else:
                chunks = form.cleaned_data['chunks']
                xdoc = parser.WLDocument.from_string(current.data('xml'))
                errors = xdoc.merge_chunks(chunks)

                if len(errors):
                    return response.EntityConflict().django_response({
                            "reason": "invalid-chunks",
                            "message": "Unable to merge following parts into the document: %s " % ",".join(errors)
                    })

                data = xdoc.serialize()

            # try to find any Xinclude tags
            includes = [m.groupdict()['link'] for m in (re.finditer(\
                XINCLUDE_REGEXP, data, flags=re.UNICODE) or []) ]

            log.info("INCLUDES: %s", includes)

            # TODO: provide useful routines to make this simpler
            def xml_update_action(lib, resolve):
                try:
                    f = lib._fileopen(resolve('parts'), 'r')
                    stored_includes = json.loads(f.read())
                    f.close()
                except:
                    stored_includes = []

                if stored_includes != includes:
                    f = lib._fileopen(resolve('parts'), 'w+')
                    f.write(json.dumps(includes))
                    f.close()

                    lib._fileadd(resolve('parts'))

                    # update the parts cache
                    PartCache.update_cache(docid, current.owner,\
                        stored_includes, includes)

                # now that the parts are ok, write xml
                f = lib._fileopen(resolve('xml'), 'w+')
                f.write(data.encode('utf-8'))
                f.close()

            ndoc = None
            ndoc = current.invoke_and_commit(\
                xml_update_action, lambda d: (msg, user) )

            try:
                # return the new revision number
                return response.SuccessAllOk().django_response({
                    "document": ndoc.id,
                    "user": user,
                    "subview": "xml",
                    "previous_revision": current.revision,
                    "revision": ndoc.revision,
                    'timestamp': ndoc.revision.timestamp,
                    "url": reverse("doctext_view", args=[ndoc.id])
                })
            except Exception, e:
                if ndoc: lib._rollback()
                raise e
        except RevisionNotFound, e:
            return response.EntityNotFound(mimetype="text/plain").\
                django_response(e.message)
