# -*- coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('wiki_img.views',
    url(r'^edit/(?P<slug>[^/]+)/$',
        'editor', name="wiki_img_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/$',
        'editor_readonly', name="wiki_img_editor_readonly"),

    url(r'^text/(?P<image_id>\d+)/$',
        'text', name="wiki_img_text"),

    url(r'^history/(?P<object_id>\d+)/$',
        'history', name="wiki_img_history"),

    url(r'^revert/(?P<object_id>\d+)/$',
        'revert', name='wiki_img_revert'),

    url(r'^diff/(?P<object_id>\d+)/$', 'diff', name="wiki_img_diff"),
    url(r'^pubmark/(?P<object_id>\d+)/$', 'pubmark', name="wiki_img_pubmark"),

)
