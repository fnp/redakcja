# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
import django_cas_ng.views



urlpatterns = [
    #url(r'^admin/login/$', django_cas_ng.views.login, name='login'),
    #url(r'^admin/logout/$', django_cas_ng.views.logout, name='logout'),

    # Admin panel
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('catalogue/', include('catalogue.urls')),
    path('', RedirectView.as_view(url='/documents/', permanent=False)),
    path('documents/', include('documents.urls')),
    path('apiclient/', include('apiclient.urls')),
    path('editor/', include('wiki.urls')),
    path('images/', include('wiki_img.urls')),
    path('cover/', include('cover.urls')),
    path('depot/', include('depot.urls')),
    path('wlxml/', include('wlxml.urls')),
    path('isbn/', include('isbn.urls')),
    path('sources/', include('sources.urls')),

    path('api/', include('redakcja.api.urls')),
]


if settings.CAS_SERVER_URL:
    urlpatterns += [
        path('accounts/login/', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
        path('accounts/logout/', django_cas_ng.views.LogoutView.as_view(), name='logout'),
    ]
else:
    import django.contrib.auth.views
    urlpatterns += [
        path('accounts/login/', django.contrib.auth.views.LoginView.as_view(), name='cas_ng_login'),
        path('accounts/', include('django.contrib.auth.urls')),
    ]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
