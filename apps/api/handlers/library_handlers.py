# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

import settings
import librarian
import api.forms as forms
from datetime import date

from django.core.urlresolvers import reverse
from wlrepo import MercurialLibrary, RevisionNotFound

from librarian import dcparser

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

    def create(self, request):
        """Create a new document."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)

        form = forms.DocumentUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return rc.BAD_REQUEST

        f = request.FILES['ocr']
        data = f.read().decode('utf-8')

        if form.cleaned_data['generate_dc']:
            data = librarian.wrap_text(data, unicode(date.today()))

        # TODO: what if the file exists ?
        doc = lib.document_create(form.cleaned_data['bookname'])
        doc.quickwrite('xml', data, '$AUTO$ XML data uploaded.',
            user=request.user.username)

        return {
            'url': reverse('document_view', args=[doc.id]),
            'name': doc.id,
            'revision': doc.revision }

#
# Document Handlers
#
class BasicDocumentHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, docid):
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)

        opts = forms.DocumentGetForm(request.GET)
        if not opts.is_valid():
            return rc.BAD_REQUEST

        doc = lib.document(docid)

        result = {
            'name': doc.id,
            'text_url': reverse('doctext_view', args=[doc.id]),
            'dc_url': reverse('docdc_view', docid=doc.id),
            'latest_rev': doc.revision,
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

        opts = forms.DocumentGetForm(request.GET)
        if not opts.is_valid():
            return rc.BAD_REQUEST

        try:
            doc = lib.document(docid)
            udoc = doc.take(request.user.username)
        except RevisionNotFound:
            return rc.NOT_HERE

        # is_shared = udoc.ancestorof(doc)
        # is_uptodate = is_shared or shared.ancestorof(document)

        result = {
            'name': udoc.id,
            'text_url': reverse('doctext_view', args=[udoc.id]),
            'dc_url': reverse('docdc_view', args=[udoc.id]),
            'parts_url': reverse('docparts_view', args=[udoc.id]),
            'latest_rev': udoc.revision,
            'latest_shared_rev': doc.revision,
            # 'shared': is_shared,
            # 'up_to_date': is_uptodate,
        }

        #if request.GET.get('with_part', 'no') == 'yes':
        #    result['parts'] = document.parts()

        return result

#
# Document Text View
#
class DocumentTextHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self, request, docid):
        """Read document as raw text"""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            return lib.document(docid, request.user.username).data('xml')
        except RevisionNotFound:
            return rc.NOT_HERE

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
                return rc.DUPLICATE_ENTRY

            doc.quickwrite('xml', data, msg)

            return rc.ALL_OK
        except (RevisionNotFound, KeyError):
            return rc.NOT_HERE

#
# Dublin Core handlers
#
# @requires librarian
#
class DocumentDublinCoreHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self, request, docid):
        """Read document as raw text"""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            doc = lib.document(docid, request.user.username).data('xml')
            bookinfo = dcparser.BookInfo.from_string(doc.read())

            return bookinfo.serialize()
        except RevisionNotFound:
            return rc.NOT_HERE

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
                return rc.DUPLICATE_ENTRY

            xmldoc = parser.WLDocument.from_string(current.data('xml'))
            document.book_info = dcparser.BookInfo.from_json(bi_json)

            # zapisz
            current.quickwrite('xml', document.serialize().encode('utf-8'),\
                message=msg, user=request.user.username)

            return rc.ALL_OK
        except (RevisionNotFound, KeyError):
            return rc.NOT_HERE
