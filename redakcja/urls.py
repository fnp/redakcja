# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
    # Auth
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'catalogue.views.logout_then_redirect', name='logout'),

    # Admin panel
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^comments/', include('django.contrib.comments.urls')),

    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/documents/'}),
    url(r'^documents/', include('catalogue.urls')),
    url(r'^apiclient/', include('apiclient.urls')),
    url(r'^editor/', include('wiki.urls')),

    # Static files (should be served by Apache)
    url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.+)$' % settings.ADMIN_MEDIA_PREFIX[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),

    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/documents/'}),

)
