from django.conf import settings


WL_CONSUMER_KEY = getattr(settings, 'APICLIENT_WL_CONSUMER_KEY', None)
WL_CONSUMER_SECRET = getattr(settings, 'APICLIENT_WL_CONSUMER_SECRET', None)

WL_API_URL = getattr(settings, 'APICLIENT_WL_API_URL', 'https://wolnelektury.pl/api/')

BETA_API_URL = getattr(settings, 'APICLIENT_BETA_API_URL', 'http://dev.wolnelektury.pl/api/')

WL_REQUEST_TOKEN_URL = getattr(settings, 'APICLIENT_WL_REQUEST_TOKEN_URL', 
        WL_API_URL + 'oauth/request_token/')
WL_ACCESS_TOKEN_URL = getattr(settings, 'APICLIENT_WL_ACCESS_TOKEN_URL', 
        WL_API_URL + 'oauth/access_token/')
WL_AUTHORIZE_URL = getattr(settings, 'APICLIENT_WL_AUTHORIZE_URL', 
        WL_API_URL + 'oauth/authorize/')

BETA_REQUEST_TOKEN_URL = BETA_API_URL + 'oauth/request_token/'
BETA_ACCESS_TOKEN_URL = BETA_API_URL + 'oauth/access_token/'
BETA_AUTHORIZE_URL = BETA_API_URL + 'oauth/authorize/'
