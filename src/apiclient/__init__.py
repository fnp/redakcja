# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from urllib.parse import urlencode
import oauth2
from apiclient.settings import WL_CONSUMER_KEY, WL_CONSUMER_SECRET, WL_API_URL, BETA_API_URL


if WL_CONSUMER_KEY and WL_CONSUMER_SECRET:
    wl_consumer = oauth2.Consumer(WL_CONSUMER_KEY, WL_CONSUMER_SECRET)
else:
    wl_consumer = None


class ApiError(BaseException):
    pass


class NotAuthorizedError(BaseException):
    pass


def api_call(user, path, data=None, beta=False, method=None, as_json=False):
    from .models import OAuthConnection
    api_url = BETA_API_URL if beta else WL_API_URL
    conn = OAuthConnection.get(user=user, beta=beta)
    if not conn.access:
        raise NotAuthorizedError("No WL authorization for user %s." % user)
    token = oauth2.Token(conn.token, conn.token_secret)
    client = oauth2.Client(wl_consumer, token)
    if data is not None:
        data = json.dumps(data)
        headers = {}
        if as_json:
            headers["Content-Type"] = 'application/json'
        else:
            data = urlencode({"data": data})
        data = data.encode('utf-8')

        resp, content = client.request(
            "%s%s" % (api_url, path),
            method=method or 'POST',
            headers=headers,
            body=data)
    else:
        resp, content = client.request(
            "%s%s" % (api_url, path),
            method=method or 'GET'
        )
    status = resp['status']

    if status in ('200', '201'):
        return json.loads(content)
    elif status.startswith('2'):
        return
    elif status == '401':
        raise ApiError('User not authorized for publishing.')
    else:
        raise ApiError("WL API call error %s, path: %s, body: %s" % (status, path, content))
