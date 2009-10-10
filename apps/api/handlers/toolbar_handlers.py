# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 15:55:33$"
__doc__ = "Module documentation."

from django.views.generic.simple import direct_to_template
from piston.handler import BaseHandler
from piston.utils import rc

import settings

import toolbar.models

class ToolbarHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        groups = toolbar.models.ButtonGroup.objects.all()
        return [g.to_dict(with_buttons=True) for g in groups]
            
class ScriptletsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        scriptlets = toolbar.models.Scriptlet.objects.all()

        return direct_to_template(request, 'toolbar_api/scriptlets.js',
            extra_context = {'scriptlets': scriptlets },
            mimetype='text/javascript' )