# -*- coding: utf-8
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.list_detail import object_list

from wiki_img.models import ImageDocument


PART = ur"""[ ĄĆĘŁŃÓŚŻŹąćęłńóśżź0-9\w_.-]+"""

urlpatterns = patterns('wiki_img.views',
    url(r'^$', object_list, {'queryset': ImageDocument.objects.all(), "template_name": "wiki_img/document_list.html"}),

    url(r'^edit/(?P<slug>%s)$' % PART,
        'editor', name="wiki_img_editor"),

    url(r'^(?P<slug>[^/]+)/text$',
        'text', name="wiki_img_text"),

)
