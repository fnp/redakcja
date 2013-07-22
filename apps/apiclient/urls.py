from django.conf.urls import patterns, url

urlpatterns = patterns('apiclient.views',
    url(r'^oauth/$', 'oauth', name='apiclient_oauth'),
    url(r'^oauth_callback/$', 'oauth_callback', name='apiclient_oauth_callback'),
)
