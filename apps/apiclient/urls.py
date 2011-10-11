from django.conf.urls.defaults import *

urlpatterns = patterns('apiclient.views',
    url(r'^oauth/$', 'oauth', name='apiclient_oauth'),
    url(r'^oauth_callback/$', 'oauth_callback', name='apiclient_oauth_callback'),
)
