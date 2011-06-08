from django.conf.urls.defaults import *

urlpatterns = patterns('apiclient.views',
    url(r'^oauth/$', 'oauth', name='users_oauth'),
    url(r'^oauth_callback/$', 'oauth_callback', name='users_oauth_callback'),
)
