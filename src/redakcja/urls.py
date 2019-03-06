# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
import django_cas.views


admin.autodiscover()

urlpatterns = [
    # Auth
    url(r'^accounts/login/$', django_cas.views.login, name='login'),
    url(r'^accounts/logout/$', django_cas.views.logout, name='logout'),
    url(r'^admin/login/$', django_cas.views.login, name='login'),
    url(r'^admin/logout/$', django_cas.views.logout, name='logout'),

    # Admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', RedirectView.as_view(url= '/documents/', permanent=False)),
    url(r'^documents/', include('catalogue.urls')),
    url(r'^apiclient/', include('apiclient.urls')),
    url(r'^editor/', include('wiki.urls')),
    url(r'^images/', include('wiki_img.urls')),
    url(r'^cover/', include('cover.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns += (url(r'^__debug__/', include(debug_toolbar.urls))),
