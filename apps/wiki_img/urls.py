# -*- coding: utf-8
from django.conf.urls.defaults import *


urlpatterns = patterns('wiki_img.views',
    url(r'^edit/(?P<slug>[^/]+)/$',
        'editor', name="wiki_img_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/$',
        'editor_readonly', name="wiki_img_editor_readonly"),

    url(r'^text/(?P<image_id>\d+)/$',
        'text', name="wiki_img_text"),

    url(r'^history/(?P<chunk_id>\d+)/$',
        'history', name="wiki_history"),

)
