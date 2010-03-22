import os

from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, Http404
from django.utils import simplejson as json

from wiki.models import Document, DocumentNotFound, getstorage
from wiki.forms import DocumentForm
from datetime import datetime
from django.utils.encoding import smart_unicode

#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

import logging
logger = logging.getLogger("fnp.peanut.api")

import nice_diff
import operator

MAX_LAST_DOCS = 10

class DateTimeEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, datetime):
             return datetime.ctime(obj) + " " + (datetime.tzname(obj) or 'GMT')
         return json.JSONEncoder.default(self, obj)

@never_cache
def document_list(request, template_name = 'wiki/document_list.html'):
    # TODO: find a way to cache "Storage All"
    return direct_to_template(request, template_name, extra_context = {
        'document_list': getstorage().all(),
        'last_docs': sorted(request.session.get("wiki_last_docs", {}).items(), 
                        key=operator.itemgetter(1), reverse = True)
    })  

@never_cache
def document_detail(request, name, template_name = 'wiki/document_details.html'):
    print "Trying to get", repr(name)
    try:
        document = getstorage().get(name)
    except DocumentNotFound:        
        raise Http404
    
    access_time = datetime.now()
    last_documents = request.session.get("wiki_last_docs", {})      
    last_documents[name] = access_time
    
    if len(last_documents) > MAX_LAST_DOCS:
        oldest_key = min(last_documents, key = last_documents.__getitem__)
        del last_documents[oldest_key]        
    request.session['wiki_last_docs'] = last_documents   
                
    if request.method == 'POST':        
        form = DocumentForm(request.POST, instance = document)
        if form.is_valid():
            document = form.save(document_author = request.user.username)
            return HttpResponse(json.dumps({'text': document.plain_text, 'meta': document.meta(), 'revision': document.revision()}))
        else:
            return HttpResponse(json.dumps({'errors': form.errors}))
    else:
        form = DocumentForm(instance = document)

    return direct_to_template(request, template_name, extra_context = {
        'document': document,
        'form': form,
    })


@never_cache
def document_gallery(request, directory):
    try:
        base_dir = os.path.join(
                    smart_unicode(settings.MEDIA_ROOT), 
                    smart_unicode(settings.FILEBROWSER_DIRECTORY),
                    smart_unicode(directory) )
        
        def map_to_url(filename):           
                         
            return '%s%s%s/%s' % (
                        smart_unicode(settings.MEDIA_URL),                         
                        smart_unicode(settings.FILEBROWSER_DIRECTORY),
                        smart_unicode(directory),
                        smart_unicode(filename)
            )
            
        def is_image(filename):
            return os.path.splitext(f)[1].lower() in (u'.jpg', u'.jpeg', u'.png')
            
        images = [ map_to_url(f) for f in map(smart_unicode, os.listdir(base_dir)) if is_image(f) ]
        images.sort()
        return HttpResponse(json.dumps(images))
    except (IndexError, OSError), exc:
        import traceback
        traceback.print_exc()

        raise Http404
    
@never_cache
def document_diff(request, name, revA, revB):
    storage = getstorage()     
    docA = storage.get(name, int(revA))
    docB = storage.get(name, int(revB)) 
    
    
    return HttpResponse(nice_diff.html_diff_table(docA.plain_text.splitlines(), 
                                         docB.plain_text.splitlines()) )                                           
    
@never_cache    
def document_history(request, name):
    storage = getstorage()
    
    return HttpResponse( 
                json.dumps(storage.history(name), cls=DateTimeEncoder), 
                mimetype='application/json')
    
    
import urllib, urllib2

@never_cache
def document_publish(request, name, version):
    storage = getstorage()
    
    # get the document
    try:
        document = storage.get(name, revision = int(version))
    except DocumentNotFound:        
        raise Http404
    
    auth_handler = urllib2.HTTPDigestAuthHandler();
    auth_handler.add_password(
                    realm="localhost:8000",
                    uri="http://localhost:8000/api/",
                    user="test", passwd="test")
    
    
    opener = urllib2.build_opener(auth_handler)         
    rq = urllib2.Request("http://localhost:8000/api/books.json")
    rq.add_data(json.dumps({"text": document.text, "compressed": False}))
    rq.add_header("Content-Type", "application/json")
    
    try:
        response = opener.open(rq)                 
        result = {"success": True, "message": response.read()}        
    except urllib2.HTTPError, e:
        logger.exception("Failed to send")
        if e.code == 500:
            return HttpResponse(e.read(), mimetype='text/plain')                        
        result = {"success": False, "reason": e.read(), "errno": e.code}
        
    return HttpResponse( json.dumps(result), mimetype='application/json')       