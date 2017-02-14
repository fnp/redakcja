# -*- coding: utf-8
from django.conf.urls import url
from wiki import views

urlpatterns = (
    url(r'^edit/(?P<pk>[^/]+)/$', views.editor, name="wiki_editor"),

    url(r'^gallery/(?P<directory>[^/]+)/$', views.gallery, name="wiki_gallery"),

    url(r'^history/(?P<doc_id>\d+)/$', views.history, name="wiki_history"),

    url(r'^text/(?P<doc_id>\d+)/$', views.text, name="wiki_text"),

    url(r'^revert/(?P<doc_id>\d+)/$', views.revert, name='wiki_revert'),

    url(r'^diff/(?P<doc_id>\d+)/$', views.diff, name="wiki_diff"),
)
