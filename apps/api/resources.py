# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:53:00$"
__doc__ = "Module documentation."

from piston.resource import Resource
from api.utils import DjangoAuth

authdata = {'authentication': DjangoAuth()}

#
# Library resources
#

import api.handlers.library_handlers as dh
from api.handlers.text_handler import DocumentTextHandler

library_resource = Resource(dh.LibraryHandler, **authdata)
document_resource = Resource(dh.DocumentHandler, **authdata)
document_text_resource = Resource(DocumentTextHandler, **authdata)
document_html_resource = Resource(dh.DocumentHTMLHandler, **authdata)
# document_dc_resource = Resource(dh.DocumentDublinCoreHandler, **authdata)
document_gallery = Resource(dh.DocumentGalleryHandler, **authdata)
document_merge = Resource(dh.MergeHandler, **authdata)
diff_resource = Resource(dh.DiffHandler, **authdata)

import api.handlers.manage_handlers as mh

pullrequest_collection = Resource(mh.PullRequestListHandler, **authdata)
pullrequest_rsrc = Resource(mh.PullRequestHandler, **authdata)

#
# Toolbar resources
#
import api.handlers.toolbar_handlers as th
toolbar_buttons = Resource(th.ToolbarHandler, **authdata)
scriptlets = Resource(th.ScriptletsHandler, **authdata)



__all__ = [
    'library_resource',
    'document_resource',
    'document_text_resource',
    'document_html_resource',
#    'document_dc_resource',
    'document_gallery',
    'document_merge',
    'toolbar_buttons',
    'scriptlets',
    'pullrequest_collection',
    'pullrequest_rsrc',
    'diff_resource',
]