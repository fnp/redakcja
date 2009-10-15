# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-26 00:32:18$"
__doc__ = "Extensible HTTP Responses."

from django.http import HttpResponse
from django.utils import simplejson as json

MIME_PLAIN = 'text/plain'
MIME_JSON = 'application/json'

class ResponseObject(object):

    def __init__(self, code, mimetype=MIME_JSON):
        self._code = code
        self._mime = mimetype        

    def django_response(self, body=None):
        if body is None:
            data = ''
        elif self._mime == MIME_JSON:
            data = json.dumps(body, default=lambda o: repr(o) )
        else:
            # data = u"%s\n%s" % (self.MESSAGE, unicode(body))
            data = unicode(body).encode('utf-8')
            
        return HttpResponse(content=data, status=self._code, \
                content_type=self._mime+'; charset=utf-8' )        
    
class SuccessAllOk(ResponseObject):
    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 200, **kwargs)
        
class EntityCreated(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 201, **kwargs)

    def django_response(self, url, body):        
        response = ResponseObject.django_response(self, body)
        response['Location'] = url
        return response

class RequestAccepted(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 202, **kwargs)

    def django_response(self, ticket_status, ticket_uri):
        return ResponseObject.django_response(self, {
            'status': ticket_status,
            'refer_to': ticket_uri })     
        
class SuccessNoContent(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 204, **kwargs)

    def django_response(self):
        return ResponseObject.django_response(self, body=None)

#
# Client errors
#

class BadRequest(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 400, **kwargs)
    
class AccessDenied(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 403, **kwargs)
    

class EntityNotFound(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 404, **kwargs)

class EntityGone(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 410, **kwargs)


class EntityConflict(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 409, **kwargs)


#
# Server side errors
#
class InternalError(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 500, **kwargs)

class NotImplemented(ResponseObject):

    def __init__(self, **kwargs):
        ResponseObject.__init__(self, 501, **kwargs) 