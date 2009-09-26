# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler


import librarian
import librarian.html
import api.forms as forms
from datetime import date

from django.core.urlresolvers import reverse

from wlrepo import RevisionNotFound, LibraryException, DocumentAlreadyExists
from librarian import dcparser

import api.response as response
from api.utils import validate_form, hglibrary

from explorer.models import PullRequest

#
# Document List Handlers
#
class BasicLibraryHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    @hglibrary
    def read(self, request, lib):
        """Return the list of documents."""       
        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in lib.documents() ]

        return {'documents' : document_list}
        

class LibraryHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    anonymous = BasicLibraryHandler

    @hglibrary
    def read(self, request, lib):
        """Return the list of documents."""

        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in lib.documents() ]

        return {'documents' : document_list }        

    @validate_form(forms.DocumentUploadForm, 'POST')
    @hglibrary
    def create(self, request, form, lib):
        """Create a new document."""       

        if form.cleaned_data['ocr_data']:
            data = form.cleaned_data['ocr_data']
        else:            
            data = request.FILES['ocr_file'].read().decode('utf-8')

        if form.cleaned_data['generate_dc']:
            data = librarian.wrap_text(data, unicode(date.today()))

        docid = form.cleaned_data['bookname']

        try:
            lock = lib.lock()            
            try:
                doc = lib.document_create(docid)
                # document created, but no content yet

                try:
                    doc = doc.quickwrite('xml', data.encode('utf-8'),
                        '$AUTO$ XML data uploaded.', user=request.user.username)
                except Exception,e:
                    # rollback branch creation
                    lib._rollback()
                    raise LibraryException("Exception occured:" + repr(e))

                url = reverse('document_view', args=[doc.id])

                return response.EntityCreated().django_response(\
                    body = {
                        'url': url,
                        'name': doc.id,
                        'revision': doc.revision },
                    url = url )            
            finally:
                lock.release()
        except LibraryException, e:
            return response.InternalError().django_response(\
                {'exception': repr(e) })                
        except DocumentAlreadyExists:
            # Document is already there
            return response.EntityConflict().django_response(\
                {"reason": "Document %s already exists." % docid})

#
# Document Handlers
#
class BasicDocumentHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    @hglibrary
    def read(self, request, docid, lib):
        try:    
            doc = lib.document(docid)
        except RevisionNotFound:
            return rc.NOT_FOUND

        result = {
            'name': doc.id,
            'html_url': reverse('dochtml_view', args=[doc.id,doc.revision]),
            'text_url': reverse('doctext_view', args=[doc.id,doc.revision]),
            'dc_url': reverse('docdc_view', args=[doc.id,doc.revision]),
            'public_revision': doc.revision,
        }

        return result

#
# Document Meta Data
#
class DocumentHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    anonymous = BasicDocumentHandler

    @hglibrary
    def read(self, request, docid, lib):
        """Read document's meta data"""       
        try:
            doc = lib.document(docid)
            udoc = doc.take(request.user.username)
        except RevisionNotFound:
            return request.EnityNotFound().django_response()

        # is_shared = udoc.ancestorof(doc)
        # is_uptodate = is_shared or shared.ancestorof(document)

        result = {
            'name': udoc.id,
            'html_url': reverse('dochtml_view', args=[doc.id,doc.revision]),
            'text_url': reverse('doctext_view', args=[doc.id,doc.revision]),
            'dc_url': reverse('docdc_view', args=[doc.id,doc.revision]),
            'user_revision': udoc.revision,
            'public_revision': doc.revision,            
        }       

        return result

    @hglibrary
    def update(self, request, docid, lib):
        """Update information about the document, like display not"""
        return
#
#
#

class DocumentHTMLHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    @hglibrary
    def read(self, request, docid, revision, lib):
        """Read document as html text"""
        try:
            if revision == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(revision)

            return librarian.html.transform(document.data('xml'))
        except RevisionNotFound:
            return response.EntityNotFound().django_response()

#
# Document Text View
#
class DocumentTextHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    @hglibrary
    def read(self, request, docid, revision, lib):
        """Read document as raw text"""               
        try:
            if revision == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(revision)
            
            # TODO: some finer-grained access control
            return document.data('xml')
        except RevisionNotFound:
            return response.EntityNotFound().django_response()

    @hglibrary
    def update(self, request, docid, revision, lib):
        try:
            data = request.PUT['contents']            

            if request.PUT.has_key('message'):
                msg = u"$USER$ " + request.PUT['message']
            else:
                msg = u"$AUTO$ XML content update."

            current = lib.document(docid, request.user.username)
            orig = lib.document_for_rev(revision)

            if current != orig:
                return response.EntityConflict().django_response({
                        "reason": "out-of-date",
                        "provided_revision": orig.revision,
                        "latest_revision": current.revision })

            ndoc = doc.quickwrite('xml', data, msg)

            # return the new revision number
            return {
                "document": ndoc.id,
                "subview": "xml",
                "previous_revision": prev,
                "updated_revision": ndoc.revision
            }
        
        except (RevisionNotFound, KeyError):
            return response.EntityNotFound().django_response()

#
# Dublin Core handlers
#
# @requires librarian
#
class DocumentDublinCoreHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    @hglibrary
    def read(self, request, docid, revision, lib):
        """Read document as raw text"""        
        try:
            if revision == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(revision)
            
            bookinfo = dcparser.BookInfo.from_string(doc.data('xml'))
            return bookinfo.serialize()
        except RevisionNotFound:
            return response.EntityNotFound().django_response()

    @hglibrary
    def update(self, request, docid, revision, lib):
        try:
            bi_json = request.PUT['contents']            
            if request.PUT.has_key('message'):
                msg = u"$USER$ " + request.PUT['message']
            else:
                msg = u"$AUTO$ Dublin core update."

            current = lib.document(docid, request.user.username)
            orig = lib.document_for_rev(revision)

            if current != orig:
                return response.EntityConflict().django_response({
                        "reason": "out-of-date",
                        "provided": orig.revision,
                        "latest": current.revision })

            xmldoc = parser.WLDocument.from_string(current.data('xml'))
            document.book_info = dcparser.BookInfo.from_json(bi_json)

            # zapisz
            ndoc = current.quickwrite('xml', \
                document.serialize().encode('utf-8'),\
                message=msg, user=request.user.username)

            return {
                "document": ndoc.id,
                "subview": "xml",
                "previous_revision": prev,
                "updated_revision": ndoc.revision
            }
        except (RevisionNotFound, KeyError):
            return response.EntityNotFound().django_response()


class MergeHandler(BaseHandler):
    allowed_methods = ('POST',)

    @validate_form(forms.MergeRequestForm)
    @hglibrary
    def create(self, request, form, docid, lib):
        """Create a new document revision from the information provided by user"""

        target_rev = form.cleaned_data['target_revision']

        doc = lib.document(docid)
        udoc = doc.take(request.user.username)

        if target_rev == 'latest':
            target_rev = udoc.revision

        if udoc.revision != target_rev:
            # user think doesn't know he has an old version
            # of his own branch.
            
            # Updating is teorericly ok, but we need would
            # have to force a refresh. Sharing may be not safe,
            # 'cause it doesn't always result in update.

            # In other words, we can't lie about the resource's state
            # So we should just yield and 'out-of-date' conflict
            # and let the client ask again with updated info.

            # NOTE: this could result in a race condition, when there
            # are 2 instances of the same user editing the same document.
            # Instance "A" trying to update, and instance "B" always changing
            # the document right before "A". The anwser to this problem is
            # for the "A" to request a merge from 'latest' and then
            # check the parent revisions in response, if he actually
            # merge from where he thinks he should. If not, the client SHOULD
            # update his internal state.
            return response.EntityConflict().django_response({
                    "reason": "out-of-date",
                    "provided": target_revision,
                    "latest": udoc.revision })

        if not request.user.has_permission('explorer.pull_request.can_add'):
            # User is not permitted to make a merge, right away
            # So we instead create a pull request in the database
            prq = PullRequest(
                commiter=request.uset.username,
                document=docid,
                source_revision = udoc.revision,
                status="N",
                comment = form.cleaned_data['comment']
            )

            prq.save()
            return response.RequestAccepted()

        if form.cleanded_data['type'] == 'update':
            # update is always performed from the file branch
            # to the user branch
            success, changed = udoc.update(request.user.username)

        if form.cleanded_data['type'] == 'share':
            success, changed = udoc.share(form.cleaned_data['comment'])

        if not success:
            return response.EntityConflict().django_response()

        if not changed:
            return response.SuccessNoContent().django_response()

        new_udoc = udoc.latest()

        return response.SuccessAllOk().django_response({
            "name": udoc.id,
            "parent_user_resivion": udoc.revision,
            "parent_revision": doc.revision,
            "revision": udoc.revision,
        })