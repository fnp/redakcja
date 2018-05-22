# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('apiclient.views',
    url(r'^oauth/$', 'oauth', name='apiclient_oauth'),
    url(r'^oauth_callback/$', 'oauth_callback', name='apiclient_oauth_callback'),
    url(r'^oauth-beta/$', 'oauth', kwargs={'beta': True}, name='apiclient_beta_oauth'),
    url(r'^oauth_callback-beta/$', 'oauth_callback', kwargs={'beta': True}, name='apiclient_beta_callback'),
)
