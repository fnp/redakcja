# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler


import settings
import librarian
import api.forms as forms
from datetime import date

from django.core.urlresolvers import reverse

from wlrepo import MercurialLibrary, RevisionNotFound, DocumentAlreadyExists
from librarian import dcparser

import api.response as response
from api.response import validate_form

#
# Document List Handlers
#
class BasicLibraryHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        """Return the list of documents."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)

        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in lib.documents() ]

        return {'documents' : document_list}

class LibraryHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    anonymous = BasicLibraryHandler

    def read(self, request):
        """Return the list of documents."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)

        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in lib.documents() ]

        return {'documents' : document_list }

    @validate_form(forms.DocumentUploadForm, 'POST')
    def create(self, request, form):
        """Create a new document."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)

        if form.cleaned_data['ocr_data']:
            data = form.cleaned_data['ocr_data'].encode('utf-8')
        else:            
            data = request.FILES['ocr'].read().decode('utf-8')

        if form.cleaned_data['generate_dc']:
            data = librarian.wrap_text(data, unicode(date.today()))

        docid = form.cleaned_data['bookname']
        try:
            doc = lib.document_create(docid)
            doc.quickwrite('xml', data, '$AUTO$ XML data uploaded.',
                user=request.user.username)

            url = reverse('document_view', args=[doc.id])


            return response.EntityCreated().django_response(\
                body = {
                    'url': url,
                    'name': doc.id,
                    'revision': doc.revision },
                url = url )
                
        except DocumentAlreadyExists:
            # Document is already there
            return response.EntityConflict().django_response(\
                {"reason": "Document %s already exists." % docid})

#
# Document Handlers
#
class BasicDocumentHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, docid):
        try:
            lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
            doc = lib.document(docid)
        except RevisionNotFound:
            return rc.NOT_FOUND

        result = {
            'name': doc.id,
            'text_url': reverse('doctext_view', args=[doc.id]),
            'dc_url': reverse('docdc_view', docid=doc.id),
            'public_revision': doc.revision,
        }

        return result

#
# Document Meta Data
#
class DocumentHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    anonymous = BasicDocumentHandler

    def read(self, request, docid):
        """Read document's meta data"""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        
        try:
            doc = lib.document(docid)
            udoc = doc.take(request.user.username)
        except RevisionNotFound:
            return request.EnityNotFound().django_response()

        # is_shared = udoc.ancestorof(doc)
        # is_uptodate = is_shared or shared.ancestorof(document)

        result = {
            'name': udoc.id,
            'text_url': reverse('doctext_view', args=[udoc.id]),
            'dc_url': reverse('docdc_view', args=[udoc.id]),
            'parts_url': reverse('docparts_view', args=[udoc.id]),
            'user_revision': udoc.revision,
            'public_revision': doc.revision,            
        }       

        return result

#
# Document Text View
#
class DocumentTextHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    @validate_form(forms.DocumentEntryRequest)
    def read(self, request, form, docid):
        """Read document as raw text"""        
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        
        try:
            if request.GET['revision'] == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(request.GET['revision'])
            
            # TODO: some finer-grained access control
            return document.data('xml')
        except RevisionNotFound:
            return response.EntityNotFound().django_response()

    def update(self, request, docid):
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            data = request.PUT['contents']
            prev = request.PUT['revision']

            if request.PUT.has_key('message'):
                msg = u"$USER$ " + request.PUT['message']
            else:
                msg = u"$AUTO$ XML content update."

            current = lib.document(docid, request.user.username)
            orig = lib.document_for_rev(prev)

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

    @validate_form(forms.DocumentEntryRequest)
    def read(self, request, docid):
        """Read document as raw text"""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            if request.GET['revision'] == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(request.GET['revision'])                
            
            bookinfo = dcparser.BookInfo.from_string(doc.data('xml'))
            return bookinfo.serialize()
        except RevisionNotFound:
            return response.EntityNotFound().django_response()

    def update(self, request, docid):
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            bi_json = request.PUT['contents']
            prev = request.PUT['revision']
            if request.PUT.has_key('message'):
                msg = u"$USER$ " + request.PUT['message']
            else:
                msg = u"$AUTO$ Dublin core update."

            current = lib.document(docid, request.user.username)
            orig = lib.document_for_rev(prev)

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
