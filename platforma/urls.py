# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()
PATH_SEC = r"(?P<path>[^/]+)"
PATH_END = PATH_SEC + "/$"



urlpatterns = patterns('')

if 'cas_consumer' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        # django-cas-consumer
        url(r'^accounts/login/$', 'cas_consumer.views.login', name='login'),
        url(r'^accounts/logout/$', 'cas_consumer.views.logout', name='logout'),
    )
else:
    urlpatterns += patterns('',
        # Django auth
        url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'redirect_field_name': 'next'}, name='login'),
        url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),    
    )

urlpatterns += patterns('',
    url(r'^$', 'wiki.views.document_list'),
    url(r'^gallery/(?P<directory>[^/]+)$', 'wiki.views.document_gallery'),
        
    # Admin panel
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),
    
    # Static files (should be served by Apache)
    url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
        
    url(r'^(?P<name>(.*))$', 'wiki.views.document_detail'),
    
)

