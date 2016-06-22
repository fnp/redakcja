# -*- coding: utf-8 -*-
from django.conf import settings


WL_CONSUMER_KEY = getattr(settings, 'APICLIENT_WL_CONSUMER_KEY', None)
WL_CONSUMER_SECRET = getattr(settings, 'APICLIENT_WL_CONSUMER_SECRET', None)

WL_API_URL = getattr(settings, 'APICLIENT_WL_API_URL', 'http://edukacjamedialna.edu.pl/api/')

WL_REQUEST_TOKEN_URL = getattr(settings, 'APICLIENT_WL_REQUEST_TOKEN_URL', WL_API_URL + 'oauth/request_token/')
WL_ACCESS_TOKEN_URL = getattr(settings, 'APICLIENT_WL_ACCESS_TOKEN_URL', WL_API_URL + 'oauth/access_token/')
WL_AUTHORIZE_URL = getattr(settings, 'APICLIENT_WL_AUTHORIZE_URL', WL_API_URL + 'oauth/authorize/')
