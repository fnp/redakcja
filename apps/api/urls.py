__author__="lreqc"
__date__ ="$2009-09-17 16:16:54$"

from django.conf.urls.defaults import *

from api.resources import *

FORMAT = r"\.(?P<emitter_format>xml|json|yaml)"
DOC = r'(?P<docid>[^/]+)'
REVISION = r'(?P<revision>latest|[0-9a-f]{40})'

def urlpath(*args, **kwargs):
    format = kwargs.get('format', True)
    return r'^' + (r'/'.join(args)) + (FORMAT if format else '') + '$'

urlpatterns = patterns('',
#    url(r'^hello$', hello_resource, {'emitter_format': 'json'}),
#    url(r'^hello\.(?P<emitter_format>.+)$', hello_resource),

    # Toolbar
    url(r'^toolbar/buttons$', toolbar_buttons, {'emitter_format': 'json'}),

    # Toolbar
    url(r'^toolbar/scriptlets$', scriptlets, {'emitter_format': 'json'}),
    
    # Documents
    url(r'^documents$', library_resource,
        {'emitter_format': 'json'}, name="document_list_view"),

    url(urlpath(r'documents'), library_resource,
        name="document_list_view_withformat"),
        
    url(urlpath(r'documents', DOC),
        document_resource, name="document_view_withformat"),

    url(urlpath(r'documents', DOC, format=False),
        document_resource, {'emitter_format': 'json'},
        name="document_view"),
    
    url(urlpath(r'documents', DOC, 'text', REVISION, format=False),
        document_text_resource, {'emitter_format': 'rawxml'},
        name="doctext_view"),

    url(urlpath(r'documents', DOC, 'html', REVISION, format=False),
        document_text_resource, {'emitter_format': 'rawhtml'},
        name="dochtml_view"),

    url(urlpath(r'documents', DOC, 'dc', REVISION),
        document_dc_resource,
        name="docdc_view_withformat"),

    url(urlpath(r'documents', DOC, 'dc', REVISION, format=False),
        document_dc_resource, {'emitter_format': 'json'},
        name="docdc_view"),

    url(urlpath(r'documents', DOC, 'revision'),
        document_merge, {'emitter_format': 'json'}, name="docmerge_view")

#    url(r'^documents/(?P<docid>[^/]+)/parts$',
#        document_resource, {'emitter_format': 'json'},
#        name="docparts_view"),
        
  #  url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource),
  #  url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource),
)
