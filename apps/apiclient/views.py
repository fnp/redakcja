# -*- coding: utf-8 -*-
import urlparse

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
import oauth2

from apiclient.models import OAuthConnection
from apiclient import wl_consumer
from apiclient.settings import (WL_REQUEST_TOKEN_URL, WL_ACCESS_TOKEN_URL, WL_AUTHORIZE_URL)


@login_required
def oauth(request):
    if wl_consumer is None:
        return HttpResponse("OAuth consumer not configured.")

    client = oauth2.Client(wl_consumer)
    resp, content = client.request(WL_REQUEST_TOKEN_URL)
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))
    
    conn = OAuthConnection.get(request.user)
    # this might reset existing auth!
    conn.access = False
    conn.token = request_token['oauth_token']
    conn.token_secret = request_token['oauth_token_secret']
    conn.save()

    url = "%s?oauth_token=%s&oauth_callback=%s" % (
            WL_AUTHORIZE_URL, 
            request_token['oauth_token'],
            request.build_absolute_uri(reverse("apiclient_oauth_callback")),
            )

    return HttpResponseRedirect(url)


@login_required
def oauth_callback(request):
    if wl_consumer is None:
        return HttpResponse("OAuth consumer not configured.")

    oauth_verifier = request.GET.get('oauth_verifier')
    conn = OAuthConnection.get(request.user)
    token = oauth2.Token(conn.token, conn.token_secret)
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(wl_consumer, token)
    resp, content = client.request(WL_ACCESS_TOKEN_URL, method="POST")
    access_token = dict(urlparse.parse_qsl(content))

    if 'oauth_token' in access_token:
        conn.access = True
        conn.token = access_token['oauth_token']
        conn.token_secret = access_token['oauth_token_secret']
        conn.save()
    else:
        return HttpResponse(request.GET.get('error'))

    return HttpResponseRedirect('/')
