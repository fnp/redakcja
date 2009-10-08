__author__="lreqc"
__date__ ="$2009-09-17 16:16:54$"

from django.conf.urls.defaults import *
from api.resources import *

FORMAT = r"\.(?P<emitter_format>xml|json|yaml)"
DOC = r'(?P<docid>[^/]+)'
# REVISION = r'(?P<revision>latest|[0-9a-f]{40})'

def urlpath(*args, **kwargs):
    format = kwargs.get('format', True)
    return r'^' + (r'/'.join(args)) + (FORMAT if format else '') + '$'

urlpatterns = patterns('',
#    url(r'^hello$', hello_resource, {'emitter_format': 'json'}),
#    url(r'^hello\.(?P<emitter_format>.+)$', hello_resource),

    # HTML Renderer service
    url(r'^render$', 'api.views.render'),
    
    # Toolbar
    url(r'^toolbar/buttons$', toolbar_buttons, {'emitter_format': 'json'},
        name="toolbar_buttons"
    ),
    
    url(r'^toolbar/scriptlets$', scriptlets, {'emitter_format': 'json'},
        name="toolbar_scriptlets"
    ),

    # Pull requests
    url(r"^pull-requests$", pullrequest_collection,
        {'emitter_format': 'json'} ),
        
    url(r"^pull-requests/(?P<prq_id>\d+)$", pullrequest_rsrc,
        {'emitter_format': 'json'}, name="pullrequest_view" ),    
    
    # Documents
    url(r'^documents$', library_resource,
        {'emitter_format': 'json'}, name="document_list_view"),

    url(urlpath(r'documents'), library_resource,
        name="document_list_view_withformat"),
        
    #url(urlpath(r'documents', DOC),
    #    document_resource, name="document_view_withformat"),

    url(urlpath(r'documents', DOC, format=False),
        document_resource, {'emitter_format': 'json'},
        name="document_view"),

    url(urlpath(r'documents', DOC, 'gallery', format=False),
        document_gallery, {'emitter_format': 'json'},
        name="docgallery_view"),

    # XML    
    url(urlpath(r'documents', DOC, 'text', format=False),
        document_text_resource, {'emitter_format': 'raw'},
        name="doctext_view"),

    # HTML
    url(urlpath(r'documents', DOC, 'html', format=False),
        document_html_resource, {'emitter_format': 'raw'},
        name="dochtml_view"),

    # DC
    #url(urlpath(r'documents', DOC, 'dc'),
    #    document_dc_resource,
    #    name="docdc_view_withformat"),

    url(urlpath(r'documents', DOC, 'dc', format=False),
        document_dc_resource, {'emitter_format': 'json'},
        name="docdc_view"),

    # MERGE
    url(urlpath(r'documents', DOC, 'revision', format=False),
        document_merge, {'emitter_format': 'json'}, name="docmerge_view")

#    url(r'^documents/(?P<docid>[^/]+)/parts$',
#        document_resource, {'emitter_format': 'json'},
#        name="docparts_view"),
        
  #  url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource),
  #  url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource),
)

