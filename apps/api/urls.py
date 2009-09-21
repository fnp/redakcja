__author__="lreqc"
__date__ ="$2009-09-17 16:16:54$"

from django.conf.urls.defaults import *
from piston.resource import Resource

from api.handlers import *
from api.utils import TextEmitter, DjangoAuth

authdata = {'authentication': DjangoAuth()}

FORMAT_EXT = r"\.(?P<emitter_format>xml|json|yaml|django)$"

library_resource = Resource(LibraryHandler, **authdata)
document_resource = Resource(DocumentHandler, **authdata)
document_text_resource = Resource(DocumentTextHandler, **authdata)

urlpatterns = patterns('',
#    url(r'^hello$', hello_resource, {'emitter_format': 'json'}),
#    url(r'^hello\.(?P<emitter_format>.+)$', hello_resource),

    # Documents
    url(r'^documents$', library_resource, {'emitter_format': 'json'},
        name="document_list_view"),

    url(r'^documents/(?P<docid>[^/]+)'+FORMAT_EXT,
        document_resource, name="document_view_withformat"),

    url(r'^documents/(?P<docid>[^/]+)$',
        document_resource, {'emitter_format': 'json'},
        name="document_view"),
    
    url(r'^documents/(?P<docid>[^/]+)/text$',
        document_text_resource, {'emitter_format': 'rawxml'},
        name="doctext_view"),

    url(r'^documents/(?P<docid>[^/]+)/dc$',
        document_resource, {'emitter_format': 'json'},
        name="docdc_view"),

    url(r'^documents/(?P<docid>[^/]+)/parts$',
        document_resource, {'emitter_format': 'json'},
        name="docparts_view"),
        
  #  url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource),
  #  url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource),
)

