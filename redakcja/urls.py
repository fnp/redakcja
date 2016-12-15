# -*- coding: utf-8 -*-

from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import forms_builder.forms.urls


admin.autodiscover()

urlpatterns = patterns(
    '',
    # Auth
    # url(r'^accounts/login/$', 'django_cas.views.login', name='login'),
    # url(r'^accounts/logout/$', 'django_cas.views.logout', name='logout'),
    # url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    # url(r'^accounts/logout/$', 'django.contrib.auth.views.login', name='logout'),
    # url(r'^admin/login/$', 'django_cas.views.login', name='login'),
    # url(r'^admin/logout/$', 'django_cas.views.logout', name='logout'),
    url('^accounts/', include('django.contrib.auth.urls')),

    # Admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    url(r'^$', 'redakcja.views.main'),
    url(r'^register$', 'redakcja.views.register', name='register'),
    url(r'^documents/', include('catalogue.urls')),
    url(r'^editor/', include('wiki.urls')),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^forms/', include(forms_builder.forms.urls)),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', dict(packages=['wiki'])),

)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if getattr(settings, 'SERVE_FILES_WITH_DEBUG_FALSE', False):
    urlpatterns += patterns(
        '',
        (r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],
         'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
         'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
