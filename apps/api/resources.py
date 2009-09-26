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
library_resource = Resource(dh.LibraryHandler, **authdata)
document_resource = Resource(dh.DocumentHandler, **authdata)
document_text_resource = Resource(dh.DocumentTextHandler, **authdata)
document_html_resource = Resource(dh.DocumentHTMLHandler, **authdata)
document_dc_resource = Resource(dh.DocumentDublinCoreHandler, **authdata)
document_merge = Resource(dh.MergeHandler, **authdata)

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
    'document_dc_resource',
    'document_merge',
    'toolbar_buttons',
    'scriptlets'
]