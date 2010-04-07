from django import http
from django.utils import simplejson as json
from django.utils.functional import Promise
from django.template.loader import render_to_string
from datetime import datetime

class ExtendedEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Promise):
            return unicode(obj)  
            
        if isinstance(obj, datetime):
            return datetime.ctime(obj) + " " + (datetime.tzname(obj) or 'GMT')
        
        return json.JSONEncoder.default(self, obj)

# shortcut for JSON reponses
class JSONResponse(http.HttpResponse):
    
    def __init__(self, data = {}, **kwargs):
        # get rid of mimetype
        kwargs.pop('mimetype', None)
                
        super(JSONResponse, self).__init__(
            json.dumps(data, cls=ExtendedEncoder), 
            mimetype = "application/json", **kwargs)
        

# return errors
class JSONFormInvalid(JSONResponse):
    def __init__(self, form):                 
        super(JSONFormInvalid, self).__init__(form.errors, status = 400)
    
class JSONServerError(JSONResponse):    
    def __init__(self, *args, **kwargs):
        kwargs['status'] = 500
        super(JSONServerError, self).__init__(*args, **kwargs)
    
    
    