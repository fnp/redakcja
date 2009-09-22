from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, validate

import settings
import librarian
import api.forms as forms
from datetime import date

from django.core.urlresolvers import reverse
from wlrepo import MercurialLibrary, CabinetNotFound

from librarian import dcparser

#
# Document List Handlers
#
class BasicLibraryHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        """Return the list of documents."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        cab = lib.main_cabinet

        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in cab.documents() ]

        return {
            'cabinet': cab.name,
            'latest_rev': cab.shelf(),
            'documents' : document_list }

class LibraryHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    anonymous = BasicLibraryHandler

    def read(self, request):
        """Return the list of documents."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        cab = lib.main_cabinet

        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in cab.documents() ]

        return {
            'cabinet': cab.name,
            'latest_rev': cab.shelf(),
            'documents' : document_list }

    def create(self, request):
        """Create a new document."""
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        cab = lib.main_cabinet

        form = forms.DocumentUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return rc.BAD_REQUEST

        f = request.FILES['ocr']
        data = f.read().decode('utf-8')

        if form.cleaned_data['generate_dc']:
            data = librarian.wrap_text(data, unicode(date.today()))

        doc = cab.create(form.cleaned_data['bookname'], initial_data=data)
        
        return {
            'url': reverse('document_view', args=[doc.name]),
            'name': doc.name,
            'size': doc.size,
            'revision': doc.shelf() }

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

        document = lib.main_cabinet.retrieve(docid)        

        result = {
            'name': document.name,
            'size': document.size,
            'text_url': reverse('doctext_view', args=[docid]),
            #'dc_url': reverse('docdc_view', docid=document.name),
            #'parts_url': reverse('docparts_view', docid=document.name),
            'latest_rev': document.shelf(),          
        }

        if request.GET.get('with_part', 'no') == 'yes':
            result['parts'] = document.parts()

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
              
        document = lib.cabinet(docid, request.user.username, \
                create=opts.cleaned_data['autocabinet'] ).retrieve()

        if not document:
            return rc.NOT_HERE
                
        shared = lib.main_cabinet.retrieve(docid)

        result = {
            'name': document.name,
            'size': document.size,
            'text_url': reverse('doctext_view', args=[docid]),
            'dc_url': reverse('docdc_view', args=[docid]),
            'parts_url': reverse('docparts_view', args=[docid]),
            'latest_rev': document.shelf(),
            'latest_shared_rev': shared.shelf(),
            #'shared': lib.isparentof(document, shared),
            #'up_to_date': lib.isparentof(shared, document),
        }

        if request.GET.get('with_part', 'no') == 'yes':
            result['parts'] = document.parts()

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
            return lib.document(docid, request.user.username).read()
        except CabinetNotFound:
            return rc.NOT_HERE

    def update(self, request, docid):
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            data = request.PUT['contents']
            lib.document(docid, request.user.username).write(data)
            return rc.ALL_OK
        except (CabinetNotFound, KeyError):
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
            doc = lib.document(docid, request.user.username)

            # TODO: RAL:document should support file-like ops
            bookinfo = dcparser.BookInfo.from_string(doc.read())
            return bookinfo.serialize()
        except CabinetNotFound:
            return rc.NOT_HERE

    def update(self, request, docid):
        lib = MercurialLibrary(path=settings.REPOSITORY_PATH)
        try:
            data = request.PUT['contents']
            lib.document(docid, request.user.username).write(data)
            return rc.ALL_OK
        except (CabinetNotFound, KeyError):
            return rc.NOT_HERE

