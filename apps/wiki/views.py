import os

from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, Http404
from django.utils import simplejson as json

from wiki.models import storage, Document, DocumentNotFound
from wiki.forms import DocumentForm
from datetime import datetime

# import google_diff
# import difflib
import nice_diff
import operator

MAX_LAST_DOCS = 10

class DateTimeEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, datetime):
             return datetime.ctime(obj) + " " + (datetime.tzname(obj) or 'GMT')
         return json.JSONEncoder.default(self, obj)

def document_list(request, template_name = 'wiki/document_list.html'):
    # TODO: find a way to cache "Storage All"
    return direct_to_template(request, template_name, extra_context = {
        'document_list': storage.all(),
        'last_docs': sorted(request.session.get("wiki_last_docs", {}).items(), 
                        key=operator.itemgetter(1), reverse = True)
    })  


def document_detail(request, name, template_name = 'wiki/document_details.html'):
    try:
        document = storage.get(name)
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
            document = form.save()
            return HttpResponse(json.dumps({'text': document.plain_text, 'meta': document.meta(), 'revision': document.revision()}))
        else:
            return HttpResponse(json.dumps({'errors': form.errors}))
    else:
        form = DocumentForm(instance = document)

    return direct_to_template(request, template_name, extra_context = {
        'document': document,
        'form': form,
    })


def document_gallery(request, directory):
    try:
        base_dir = os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY, directory)
        images = [u'%s%s%s/%s' % (settings.MEDIA_URL, settings.FILEBROWSER_DIRECTORY, directory, f) for f in os.listdir(base_dir) if os.path.splitext(f)[1].lower() in (u'.jpg', u'.jpeg', u'.png')]
        images.sort()
        return HttpResponse(json.dumps(images))
    except (IndexError, OSError), exc:
        import traceback
        traceback.print_exc()

        raise Http404
    
def document_diff(request, name, revA, revB):     
    docA = storage.get(name, int(revA))
    docB = storage.get(name, int(revB)) 
    
    
    return HttpResponse(nice_diff.html_diff_table(docA.plain_text.splitlines(), 
                                         docB.plain_text.splitlines()) )                                           
    
    
def document_history(reuqest, name):
    return HttpResponse( json.dumps(storage.history(name), cls=DateTimeEncoder), mimetype='application/json')
