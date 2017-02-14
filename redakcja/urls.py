# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.i18n import javascript_catalog
import forms_builder.forms.urls

import redakcja.views

admin.autodiscover()

urlpatterns = (
    # Auth
    url('^accounts/', include('django.contrib.auth.urls')),

    # Admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^$', redakcja.views.main),
    url(r'^register$', redakcja.views.register, name='register'),
    url(r'^documents/', include('catalogue.urls')),
    url(r'^editor/', include('wiki.urls')),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^forms/', include(forms_builder.forms.urls)),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', javascript_catalog, {'packages': ['wiki']}, name='javascript_catalog'),
)

if settings.DEBUG:
    urlpatterns += tuple(staticfiles_urlpatterns())
    urlpatterns += tuple(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

if getattr(settings, 'SERVE_FILES_WITH_DEBUG_FALSE', False):
    from django.views.static import serve
    urlpatterns += (
        (r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], serve, {'document_root': settings.STATIC_ROOT}),
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], serve, {'document_root': settings.MEDIA_ROOT}),
    )
