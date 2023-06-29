# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from urllib.parse import parse_qsl

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
import oauth2

from apiclient.models import OAuthConnection
from apiclient import wl_consumer
from apiclient.settings import WL_REQUEST_TOKEN_URL, WL_ACCESS_TOKEN_URL, WL_AUTHORIZE_URL
from apiclient.settings import BETA_REQUEST_TOKEN_URL, BETA_ACCESS_TOKEN_URL, BETA_AUTHORIZE_URL


@login_required
def oauth(request, beta=False):
    if wl_consumer is None:
        return HttpResponse("OAuth consumer not configured.")

    client = oauth2.Client(wl_consumer)
    resp, content = client.request(WL_REQUEST_TOKEN_URL if not beta else BETA_REQUEST_TOKEN_URL)
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(parse_qsl(content.decode('utf-8')))

    conn = OAuthConnection.get(request.user, beta)
    # this might reset existing auth!
    conn.access = False
    conn.token = request_token['oauth_token']
    conn.token_secret = request_token['oauth_token_secret']
    conn.save()

    url = "%s?oauth_token=%s&oauth_callback=%s" % (
        WL_AUTHORIZE_URL if not beta else BETA_AUTHORIZE_URL,
        request_token['oauth_token'],
        request.build_absolute_uri(reverse("apiclient_oauth_callback" if not beta else "apiclient_beta_callback")),
        )

    return HttpResponseRedirect(url)


@login_required
def oauth_callback(request, beta=False):
    if wl_consumer is None:
        return HttpResponse("OAuth consumer not configured.")

    oauth_verifier = request.GET.get('oauth_verifier')
    conn = OAuthConnection.get(request.user, beta)
    token = oauth2.Token(conn.token, conn.token_secret)
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(wl_consumer, token)
    _resp, content = client.request(WL_ACCESS_TOKEN_URL if not beta else BETA_ACCESS_TOKEN_URL, method="POST")
    access_token = dict(parse_qsl(content.decode('utf-8')))

    conn.access = True
    conn.token = access_token['oauth_token']
    conn.token_secret = access_token['oauth_token_secret']
    conn.save()

    return HttpResponseRedirect('/')


@login_required
@require_POST
def disconnect(request):
    request.user.oauthconnection_set.filter(beta=False).delete()
    return HttpResponseRedirect(reverse('documents_user'))
