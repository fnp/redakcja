# -*- encoding: utf-8 -*-
import os.path

import logging
log = logging.getLogger('platforma.api.library')

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:49:50$"
__doc__ = "Module documentation."

from piston.handler import BaseHandler, AnonymousBaseHandler
from django.http import HttpResponse

from datetime import date

from django.core.urlresolvers import reverse
from django.db import IntegrityError

import librarian
import librarian.html
import difflib
from librarian import dcparser, parser

from wlrepo import *
from api.models import PullRequest
from explorer.models import GalleryForDocument

# internal imports
import api.forms as forms
import api.response as response
from api.utils import validate_form, hglibrary, natural_order
from api.models import PartCache, PullRequest

#
import settings


def is_prq(username):
    return username.startswith('$prq-')

def prq_for_user(username):
    try:
        return PullRequest.objects.get(id=int(username[5:]))
    except:
        return None

def check_user(request, user):
    log.info("user: %r, perm: %r" % (request.user, request.user.get_all_permissions()) )
    #pull request
    if is_prq(user):
        if not request.user.has_perm('api.view_prq'):
            yield response.AccessDenied().django_response({
                'reason': 'access-denied',
                'message': "You don't have enough priviliges to view pull requests."
            })
    # other users
    elif request.user.username != user:
        if not request.user.has_perm('api.view_other_document'):
            yield response.AccessDenied().django_response({
                'reason': 'access-denied',
                'message': "You don't have enough priviliges to view other people's document."
            })
    pass

#
# Document List Handlers
#
# TODO: security check
class BasicLibraryHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    @hglibrary
    def read(self, request, lib):
        """Return the list of documents."""       
        document_list = [{
            'url': reverse('document_view', args=[docid]),
            'name': docid } for docid in lib.documents() ]
        return {'documents' : document_list}
        
#
# This handler controlls the document collection
#
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
            return response.InternalError().django_response({
                "reason": traceback.format_exc()
            })
        except DocumentAlreadyExists:
            # Document is already there
            return response.EntityConflict().django_response({
                "reason": "already-exists",
                "message": "Document already exists." % docid
            })

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


class DiffHandler(BaseHandler):
    allowed_methods = ('GET',)
    
    @hglibrary
    def read(self, request, source_revision, target_revision, lib):
        '''Return diff between source_revision and target_revision)'''
        source_document = lib.document_for_rev(source_revision)
        target_document = lib.document_for_rev(target_revision)
        print source_document,
        print target_document
        diff = difflib.unified_diff(
            source_document.data('xml').splitlines(True),
            target_document.data('xml').splitlines(True),
            'source',
            'target')
        
        return ''.join(list(diff))


#
# Document Meta Data
#
class DocumentHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    anonymous = BasicDocumentHandler

    @validate_form(forms.DocumentRetrieveForm, 'GET')
    @hglibrary
    def read(self, request, form, docid, lib):
        """Read document's meta data"""       
        log.info(u"User '%s' wants to %s(%s) as %s" % \
            (request.user.username, docid, form.cleaned_data['revision'], form.cleaned_data['user']) )

        user = form.cleaned_data['user'] or request.user.username
        rev = form.cleaned_data['revision'] or 'latest'

        for error in check_user(request, user):
            return error
            
        try:
            doc = lib.document(docid, user, rev=rev)
        except RevisionMismatch, e:
            # the document exists, but the revision is bad
            return response.EntityNotFound().django_response({
                'reason': 'revision-mismatch',
                'message': e.message,
                'docid': docid,
                'user': user,
            })
        except RevisionNotFound, e:
            # the user doesn't have this document checked out
            # or some other weird error occured
            # try to do the checkout
            try:
                if user == request.user.username:
                    mdoc = lib.document(docid)
                    doc = mdoc.take(user)
                elif is_prq(user):
                    prq = prq_for_user(user)
                    # commiter's document
                    prq_doc = lib.document_for_rev(prq.source_revision)
                    doc = prq_doc.take(user)
                else:
                    return response.EntityNotFound().django_response({
                        'reason': 'document-not-found',
                        'message': e.message,
                        'docid': docid,
                        'user': user,
                    })
            except RevisionNotFound, e:
                return response.EntityNotFound().django_response({
                    'reason': 'document-not-found',
                    'message': e.message,
                    'docid': docid,
                    'user': user
                })

        return {
            'name': doc.id,
            'user': user,
            'html_url': reverse('dochtml_view', args=[doc.id]),
            'text_url': reverse('doctext_view', args=[doc.id]),
            # 'dc_url': reverse('docdc_view', args=[doc.id]),
            'gallery_url': reverse('docgallery_view', args=[doc.id]),
            'merge_url': reverse('docmerge_view', args=[doc.id]),
            'revision': doc.revision,
            'timestamp': doc.revision.timestamp,
            # 'public_revision': doc.revision,
            # 'public_timestamp': doc.revision.timestamp,
        }   

    
#    @hglibrary
#    def update(self, request, docid, lib):
#        """Update information about the document, like display not"""
#        return
#
#
#
class DocumentHTMLHandler(BaseHandler):
    allowed_methods = ('GET')

    @validate_form(forms.DocumentRetrieveForm, 'GET')
    @hglibrary
    def read(self, request, form, docid, lib, stylesheet='partial'):
        """Read document as html text"""
        try:
            revision = form.cleaned_data['revision']
            user = form.cleaned_data['user'] or request.user.username
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

            return librarian.html.transform(document.data('xml'), is_file=False, \
                parse_dublincore=False, stylesheet=stylesheet,\
                options={
                    "with-paths": 'boolean(1)',                    
                })
                
        except (EntryNotFound, RevisionNotFound), e:
            return response.EntityNotFound().django_response({
                'reason': 'not-found', 'message': e.message})
        except librarian.ParseError, e:
            return response.InternalError().django_response({
                'reason': 'xml-parse-error', 'message': e.message })

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
                    try:
                        file = file.decode('utf-8')
                    except:
                        log.warn(u"File %r in gallery %r is not unicode. Ommiting."\
                            % (file, dirpath) )
                        file = None

                if file is not None:
                    name, ext = os.path.splitext(os.path.basename(file))

                    if ext.lower() not in [u'.png', u'.jpeg', u'.jpg']:
                        log.warn(u"Ignoring: %s %s", name, ext)
                        url = None

                    url = settings.MEDIA_URL + assoc.subpath + u'/' + file
                
                if url is None:
                    url = settings.MEDIA_URL + u'/missing.png'
                    
                gallery['pages'].append( quote(url.encode('utf-8')) )

#            gallery['pages'].sort()
            galleries.append(gallery)

        return galleries



#
# Dublin Core handlers
#
# @requires librarian
#
#class DocumentDublinCoreHandler(BaseHandler):
#    allowed_methods = ('GET', 'POST')
#
#    @hglibrary
#    def read(self, request, docid, lib):
#        """Read document as raw text"""
#        try:
#            revision = request.GET.get('revision', 'latest')
#
#            if revision == 'latest':
#                doc = lib.document(docid)
#            else:
#                doc = lib.document_for_rev(revision)
#
#
#            if document.id != docid:
#                return response.BadRequest().django_response({'reason': 'name-mismatch',
#                    'message': 'Provided revision is not valid for this document'})
#
#            bookinfo = dcparser.BookInfo.from_string(doc.data('xml'))
#            return bookinfo.serialize()
#        except (EntryNotFound, RevisionNotFound), e:
#            return response.EntityNotFound().django_response({
#                'exception': type(e), 'message': e.message})
#
#    @hglibrary
#    def create(self, request, docid, lib):
#        try:
#            bi_json = request.POST['contents']
#            revision = request.POST['revision']
#
#            if request.POST.has_key('message'):
#                msg = u"$USER$ " + request.PUT['message']
#            else:
#                msg = u"$AUTO$ Dublin core update."
#
#            current = lib.document(docid, request.user.username)
#            orig = lib.document_for_rev(revision)
#
#            if current != orig:
#                return response.EntityConflict().django_response({
#                        "reason": "out-of-date",
#                        "provided": orig.revision,
#                        "latest": current.revision })
#
#            xmldoc = parser.WLDocument.from_string(current.data('xml'))
#            document.book_info = dcparser.BookInfo.from_json(bi_json)
#
#            # zapisz
#            ndoc = current.quickwrite('xml', \
#                document.serialize().encode('utf-8'),\
#                message=msg, user=request.user.username)
#
#            try:
#                # return the new revision number
#                return {
#                    "document": ndoc.id,
#                    "subview": "dc",
#                    "previous_revision": current.revision,
#                    "revision": ndoc.revision,
#                    'timestamp': ndoc.revision.timestamp,
#                    "url": reverse("docdc_view", args=[ndoc.id])
#                }
#            except Exception, e:
#                if ndoc: lib._rollback()
#                raise e
#        except RevisionNotFound:
#            return response.EntityNotFound().django_response()

class MergeHandler(BaseHandler):
    allowed_methods = ('POST',)

    @validate_form(forms.MergeRequestForm, 'POST')
    @hglibrary
    def create(self, request, form, docid, lib):
        """Create a new document revision from the information provided by user"""
        revision = form.cleaned_data['revision']

        # fetch the main branch document
        doc = lib.document(docid)

        # fetch the base document
        user_doc = lib.document_for_rev(revision)
        base_doc = user_doc.latest()

        if base_doc != user_doc:
            return response.EntityConflict().django_response({
                "reason": "out-of-date",
                "provided": str(user_doc.revision),
                "latest": str(base_doc.revision)
            })      

        if form.cleaned_data['type'] == 'update':
            # update is always performed from the file branch
            # to the user branch
            user_doc_new = base_doc.update(request.user.username)

            if user_doc_new == user_doc:
                return response.SuccessAllOk().django_response({
                    "result": "no-op"
                })
                
            # shared document is the same
            doc_new = doc

        if form.cleaned_data['type'] == 'share':
            if not base_doc.up_to_date():
                return response.BadRequest().django_response({
                    "reason": "not-fast-forward",
                    "message": "You must first update your branch to the latest version."
                })

            if base_doc.parentof(doc) or base_doc.has_parent_from(doc):
                return response.SuccessAllOk().django_response({
                    "result": "no-op"
                })

            # check for unresolved conflicts            
            if base_doc.has_conflict_marks():
                return response.BadRequest().django_response({                    
                    "reason": "unresolved-conflicts",
                    "message": "There are unresolved conflicts in your file. Fix them, and try again."
                })

            if not request.user.has_perm('api.share_document'):
                # User is not permitted to make a merge, right away
                # So we instead create a pull request in the database
                try:
                    prq, created = PullRequest.objects.get_or_create(
                        comitter = request.user,
                        document = docid,
                        status = "N",
                        defaults = {
                            'source_revision': str(base_doc.revision),
                            'comment': form.cleaned_data['message'] or '$AUTO$ Document shared.',
                        }
                    )

                    # there can't be 2 pending request from same user
                    # for the same document
                    if not created:
                        prq.source_revision = str(base_doc.revision)
                        prq.comment = prq.comment + 'u\n\n' + (form.cleaned_data['message'] or u'')
                        prq.save()

                    return response.RequestAccepted().django_response(\
                        ticket_status=prq.status, \
                        ticket_uri=reverse("pullrequest_view", args=[prq.id]) )
                except IntegrityError:
                    return response.EntityConflict().django_response({
                        'reason': 'request-already-exist'
                    })

            changed = base_doc.share(form.cleaned_data['message'])

            # update shared version if needed
            if changed:
                doc_new = doc.latest()
            else:
                doc_new = doc

            # the user wersion is the same
            user_doc_new = base_doc

        # The client can compare parent_revision to revision
        # to see if he needs to update user's view        
        # Same goes for shared view
        
        return response.SuccessAllOk().django_response({
            "result": "success",
            "name": user_doc_new.id,
            "user": user_doc_new.owner,

            "revision": user_doc_new.revision,
            'timestamp': user_doc_new.revision.timestamp,

            "parent_revision": user_doc.revision,
            "parent_timestamp": user_doc.revision.timestamp,

            "shared_revision": doc_new.revision,
            "shared_timestamp": doc_new.revision.timestamp,

            "shared_parent_revision": doc.revision,
            "shared_parent_timestamp": doc.revision.timestamp,
        })