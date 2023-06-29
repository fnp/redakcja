# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('oauth/', views.oauth, name='apiclient_oauth'),
    path('oauth_callback/', views.oauth_callback, name='apiclient_oauth_callback'),
    path('oauth-beta/', views.oauth, kwargs={'beta': True}, name='apiclient_beta_oauth'),
    path('oauth_callback-beta/', views.oauth_callback, kwargs={'beta': True}, name='apiclient_beta_callback'),
    path('disconnect', views.disconnect, name='apiclient_disconnect'),
]
