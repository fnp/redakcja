# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^oauth/$', views.oauth, name='apiclient_oauth'),
    url(r'^oauth_callback/$', views.oauth_callback, name='apiclient_oauth_callback'),
    url(r'^oauth-beta/$', views.oauth, kwargs={'beta': True}, name='apiclient_beta_oauth'),
    url(r'^oauth_callback-beta/$', views.oauth_callback, kwargs={'beta': True}, name='apiclient_beta_callback'),
]
