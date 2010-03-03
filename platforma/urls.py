# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

if 'cas_consumer' in settings.INSTALLED_APPS:
    auth_views = 'cas_consumer.views'
else:
    auth_views = 'django.contrib.auth.views'

urlpatterns = patterns('',
    url(r'^$', 'wiki.views.document_list'),
    url(r'^gallery/(?P<directory>[^/]+)$', 'wiki.views.document_gallery'),

    # Auth
    url(r'^accounts/login/$', auth_views + '.login', name = 'login'),
    url(r'^accounts/logout/$', auth_views + '.logout', name = 'logout'),

    # Admin panel
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),

    # Static files (should be served by Apache)
    url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.+)$' % settings.ADMIN_MEDIA_PREFIX[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),

    url(r'^(?P<name>[^/]+)$', 'wiki.views.document_detail'),
)
