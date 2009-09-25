__author__="lreqc"
__date__ ="$2009-09-17 16:16:54$"

from django.conf.urls.defaults import *

from api.resources import *

FORMAT_EXT = r"\.(?P<emitter_format>xml|json|yaml)$"

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

    url(r'^documents'+FORMAT_EXT, library_resource,
        name="document_list_view_withformat"),
        
    url(r'^documents/(?P<docid>[^/]+)'+FORMAT_EXT,
        document_resource, name="document_view_withformat"),

    url(r'^documents/(?P<docid>[^/]+)$',
        document_resource, {'emitter_format': 'json'},
        name="document_view"),
    
    url(r'^documents/(?P<docid>[^/]+)/text$',
        document_text_resource, {'emitter_format': 'rawxml'},
        name="doctext_view"),

    url(r'^documents/(?P<docid>[^/]+)/dc' + FORMAT_EXT,
        document_dc_resource,
        name="docdc_view_withformat"),

    url(r'^documents/(?P<docid>[^/]+)/dc$',
        document_dc_resource, {'emitter_format': 'json'},
        name="docdc_view"),

    url(r'^documents/(?P<docid>[^/]+)/parts$',
        document_resource, {'emitter_format': 'json'},
        name="docparts_view"),
        
  #  url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource),
  #  url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource),
)

