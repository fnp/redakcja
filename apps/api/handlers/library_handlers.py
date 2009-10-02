# -*- encoding: utf-8 -*-
import os.path
import logging

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler

import re
from datetime import date

from django.core.urlresolvers import reverse
from django.utils import simplejson as json

import librarian
import librarian.html
from librarian import dcparser

from wlrepo import *
from explorer.models import PullRequest, GalleryForDocument

# internal imports
import api.forms as forms
import api.response as response
from api.utils import validate_form, hglibrary, natural_order
from api.models import PartCache

#
import settings


log = logging.getLogger('platforma.api')


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

        documents = {}
        
        for docid in lib.documents():            
            documents[docid] = {
                'url': reverse('document_view', args=[docid]),
                'name': docid,
                'parts': []
            }

        parts = PartCache.objects.defer('part_id')\
            .values_list('part_id', 'document_id').distinct()
       
        document_tree = dict(documents)

        for part, docid in parts:
            # this way, we won't display broken links
            if not documents.has_key(part):
                log.info("NOT FOUND: %s", part)
                continue

            parent = documents[docid]
            child = documents[part]

            # not top-level anymore
            document_tree.pop(part)
            parent['parts'].append(child)
        
        for doc in documents.itervalues():
            doc['parts'].sort(key=natural_order(lambda d: d['name']))
            
        return {'documents': sorted(document_tree.itervalues(),
            key=natural_order(lambda d: d['name']) ) }

    @validate_form(forms.DocumentUploadForm, 'POST')
    @hglibrary
    def create(self, request, form, lib):
        """Create a new document."""       

        if form.cleaned_data['ocr_data']:
            data = form.cleaned_data['ocr_data']
        else:            
            data = request.FILES['ocr_file'].read().decode('utf-8')

        if data is None:
            return response.BadRequest().django_response('You must pass ocr_data or ocr_file.')

        if form.cleaned_data['generate_dc']:
            data = librarian.wrap_text(data, unicode(date.today()))

        docid = form.cleaned_data['bookname']

        try:
            lock = lib.lock()            
            try:
                log.info("DOCID %s", docid)
                doc = lib.document_create(docid)
                # document created, but no content yet

                try:
                    doc = doc.quickwrite('xml', data.encode('utf-8'),
                        '$AUTO$ XML data uploaded.', user=request.user.username)
                except Exception,e:
                    import traceback
                    # rollback branch creation
                    lib._rollback()
                    raise LibraryException(traceback.format_exc())

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
            import traceback
            return response.InternalError().django_response(\
                {'exception': traceback.format_exc()} )
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
            'html_url': reverse('dochtml_view', args=[doc.id]),
            'text_url': reverse('doctext_view', args=[doc.id]),
            'dc_url': reverse('docdc_view', args=[doc.id]),
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
        log.info(u"Read %s (%s)" % (docid, type(docid)) )
        try:
            doc = lib.document(docid)
            udoc = doc.take(request.user.username)
        except RevisionNotFound, e:
            return response.EntityNotFound().django_response({
                'exception': type(e), 'message': e.message,
                'docid': docid })

        # is_shared = udoc.ancestorof(doc)
        # is_uptodate = is_shared or shared.ancestorof(document)

        result = {
            'name': udoc.id,
            'html_url': reverse('dochtml_view', args=[udoc.id]),
            'text_url': reverse('doctext_view', args=[udoc.id]),
            'dc_url': reverse('docdc_view', args=[udoc.id]),
            'gallery_url': reverse('docgallery_view', args=[udoc.id]),
            'merge_url': reverse('docmerge_view', args=[udoc.id]),
            'user_revision': udoc.revision,
            'user_timestamp': udoc.revision.timestamp,
            'public_revision': doc.revision,
            'public_timestamp': doc.revision.timestamp,
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
    allowed_methods = ('GET')

    @hglibrary
    def read(self, request, docid, lib):
        """Read document as html text"""
        try:
            revision = request.GET.get('revision', 'latest')

            if revision == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(revision)

            if document.id != docid:
                return response.BadRequest().django_response({'reason': 'name-mismatch',
                    'message': 'Provided revision refers, to document "%s", but provided "%s"' % (document.id, docid) })

            return librarian.html.transform(document.data('xml'), is_file=False, parse_dublincore=False)
        except (EntryNotFound, RevisionNotFound), e:
            return response.EntityNotFound().django_response({
                'exception': type(e), 'message': e.message})


#
# Image Gallery
#

class DocumentGalleryHandler(BaseHandler):
    allowed_methods = ('GET')
    
    
    def read(self, request, docid):
        """Read meta-data about scans for gallery of this document."""
        galleries = []
        from urllib import quote

        for assoc in GalleryForDocument.objects.filter(document=docid):
            dirpath = os.path.join(settings.MEDIA_ROOT, assoc.subpath)

            if not os.path.isdir(dirpath):
                log.warn(u"[WARNING]: missing gallery %s", dirpath)
                continue

            gallery = {'name': assoc.name, 'pages': []}
            
            for file in os.listdir(dirpath):
                if not isinstance(file, unicode):
                    log.warn(u"File %r is gallery %r is not unicode. Ommiting."\
                        % (file, dirpath) )
                    continue
                               
                name, ext = os.path.splitext(os.path.basename(file))

                if ext.lower() not in [u'.png', u'.jpeg', u'.jpg']:
                    log.info(u"Ignoring: %s %s", name, ext)
                    continue

                url = settings.MEDIA_URL + assoc.subpath + u'/' + file;
                gallery['pages'].append( quote(url.encode('utf-8')) )

            gallery['pages'].sort()
            galleries.append(gallery)

        return galleries                      

#
# Document Text View
#

XINCLUDE_REGEXP = r"""<(?:\w+:)?include\s+[^>]*?href=("|')wlrepo://(?P<link>[^\1]+?)\1\s*[^>]*?>"""
#
#
#
class DocumentTextHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    @hglibrary
    def read(self, request, docid, lib):
        """Read document as raw text"""
        revision = request.GET.get('revision', 'latest')
        try:
            if revision == 'latest':
                document = lib.document(docid)
            else:
                document = lib.document_for_rev(revision)

            if document.id != docid:
                return response.BadRequest().django_response({'reason': 'name-mismatch',
                    'message': 'Provided revision is not valid for this document'})
            
            # TODO: some finer-grained access control
            return document.data('xml')
        except (EntryNotFound, RevisionNotFound), e:
            return response.EntityNotFound().django_response({
                'exception': type(e), 'message': e.message})

    @hglibrary
    def create(self, request, docid, lib):
        try:
            data = request.POST['contents']
            revision = request.POST['revision']

            if request.POST.has_key('message'):
                msg = u"$USER$ " + request.POST['message']
            else:
                msg = u"$AUTO$ XML content update."

            current = lib.document(docid, request.user.username)
            orig = lib.document_for_rev(revision)

            if current != orig:
                return response.EntityConflict().django_response({
                        "reason": "out-of-date",
                        "provided_revision": orig.revision,
                        "latest_revision": current.revision })

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
                xml_update_action, lambda d: (msg, current.owner) )

            try:
                # return the new revision number
                return response.SuccessAllOk().django_response({
                    "document": ndoc.id,
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


#
# Dublin Core handlers
#
# @requires librarian
#
class DocumentDublinCoreHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    @hglibrary
    def read(self, request, docid, lib):
        """Read document as raw text"""        
        try:
            revision = request.GET.get('revision', 'latest')

            if revision == 'latest':
                doc = lib.document(docid)
            else:
                doc = lib.document_for_rev(revision)


            if document.id != docid:
                return response.BadRequest().django_response({'reason': 'name-mismatch',
                    'message': 'Provided revision is not valid for this document'})
            
            bookinfo = dcparser.BookInfo.from_string(doc.data('xml'))
            return bookinfo.serialize()
        except (EntryNotFound, RevisionNotFound), e:
            return response.EntityNotFound().django_response({
                'exception': type(e), 'message': e.message})

    @hglibrary
    def create(self, request, docid, lib):
        try:
            bi_json = request.POST['contents']
            revision = request.POST['revision']
            
            if request.POST.has_key('message'):
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

            try:
                # return the new revision number
                return {
                    "document": ndoc.id,
                    "subview": "dc",
                    "previous_revision": current.revision,
                    "revision": ndoc.revision,
                    'timestamp': ndoc.revision.timestamp,
                    "url": reverse("docdc_view", args=[ndoc.id])
                }
            except Exception, e:
                if ndoc: lib._rollback()
                raise e
        except RevisionNotFound:
            return response.EntityNotFound().django_response()

class MergeHandler(BaseHandler):
    allowed_methods = ('POST',)

    @validate_form(forms.MergeRequestForm, 'POST')
    @hglibrary
    def create(self, request, form, docid, lib):
        """Create a new document revision from the information provided by user"""

        target_rev = form.cleaned_data['target_revision']

        doc = lib.document(docid)
        udoc = doc.take(request.user.username)

        if target_rev == 'latest':
            target_rev = udoc.revision

        if str(udoc.revision) != target_rev:
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
                    "provided": target_rev,
                    "latest": udoc.revision })

        if not request.user.has_perm('explorer.book.can_share'):
            # User is not permitted to make a merge, right away
            # So we instead create a pull request in the database
            prq = PullRequest(
                comitter=request.user,
                document=docid,
                source_revision = str(udoc.revision),
                status="N",
                comment = form.cleaned_data['message'] or '$AUTO$ Document shared.'
            )

            prq.save()
            return response.RequestAccepted().django_response(\
                ticket_status=prq.status, \
                ticket_uri=reverse("pullrequest_view", args=[prq.id]) )

        if form.cleaned_data['type'] == 'update':
            # update is always performed from the file branch
            # to the user branch
            success, changed = udoc.update(request.user.username)

        if form.cleaned_data['type'] == 'share':
            success, changed = udoc.share(form.cleaned_data['message'])

        if not success:
            return response.EntityConflict().django_response({
                'reason': 'merge-failure',
            })

        if not changed:
            return response.SuccessNoContent().django_response()

        nudoc = udoc.latest()

        return response.SuccessAllOk().django_response({
            "name": nudoc.id,
            "parent_user_resivion": udoc.revision,
            "parent_revision": doc.revision,
            "revision": nudoc.revision,
            'timestamp': nudoc.revision.timestamp,
        })
