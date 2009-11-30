# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()
PATH_SEC = r"(?P<path>[^/]+)"
PATH_END = PATH_SEC + "/$"

urlpatterns = patterns('',
    # Explorer:
    url(r'^$', 'explorer.views.file_list', name='file_list'),        
    url(r'^file/upload', 'explorer.views.file_upload', name='file_upload'),    

    url(r'^management/pull-requests$', 'explorer.views.pull_requests'),
  
    # Editor panels
    url(r'^editor/'+PATH_END, 'explorer.views.display_editor', name='editor_view'),
    url(r'^editor/$', 'explorer.views.file_list', name='editor_base'),

    url(r'^file/(?P<docid>[^/]+)/print$', 'explorer.views.print_html', name="file_print"),

    # Admin panel
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),

    # Theme database
    url(r'themes/', include('bookthemes.urls')),

    # Our über-restful api
    # url(r'^api/', include('api.urls')),
    
    # Static files (should be served by Apache)
    url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
        
    url(r'^(?P<name>(.*))$', 'wiki.views.document_detail'),
    
)

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
