# -*- coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('dvcs.views',
    url(r'^data/(?P<document_id>[^/]+)/(?P<version>.*)$', 'document_data', name='storage_document_data'),
)
