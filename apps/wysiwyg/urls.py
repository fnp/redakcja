# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-23 15:57:38$"
__doc__ = "Module documentation."

from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^$', 'wysiwyg.views.index'),
)
