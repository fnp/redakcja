# -*- coding: utf-8
from django.conf.urls import patterns, url
from organizations import views


urlpatterns = patterns(
    '',
    url(r'^$', views.organizations, name="organizations"),
    url(r'^new/$', views.org_new, name="organizations_new"),
    url(r'^(?P<pk>\d+)/$', views.main, name="organizations_main"),
    url(r'^(?P<pk>\d+)/members/$', views.main, {'tab': 'members'}, name="organizations_members"),
    url(r'^(?P<pk>\d+)/edit/$', views.edit, name="organizations_edit"),
    url(r'^(?P<pk>\d+)/join/$', views.join, name="organizations_join"),
    url(r'^(?P<pk>\d+)/membership/$', views.membership, name="organizations_membership"),

    url(r'^people/(?P<pk>\d+)/$', views.user_card, name="organizations_user"),
    url(r'^people/me/$', views.user_edit, name="organizations_user_edit"),
)
