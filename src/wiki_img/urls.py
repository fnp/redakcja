# -*- coding: utf-8
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^edit/(?P<slug>[^/]+)/$',
        views.editor, name="wiki_img_editor"),

    url(r'^readonly/(?P<slug>[^/]+)/$',
        views.editor_readonly, name="wiki_img_editor_readonly"),

    url(r'^text/(?P<image_id>\d+)/$',
        views.text, name="wiki_img_text"),

    url(r'^history/(?P<object_id>\d+)/$',
        views.history, name="wiki_img_history"),

    url(r'^revert/(?P<object_id>\d+)/$',
        views.revert, name='wiki_img_revert'),

    url(r'^diff/(?P<object_id>\d+)/$', views.diff, name="wiki_img_diff"),
    url(r'^pubmark/(?P<object_id>\d+)/$', views.pubmark, name="wiki_img_pubmark"),
]
