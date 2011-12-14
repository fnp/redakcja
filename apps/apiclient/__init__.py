import urllib

from django.utils import simplejson
import oauth2

from apiclient.models import OAuthConnection
from apiclient.settings import WL_CONSUMER_KEY, WL_CONSUMER_SECRET, WL_API_URL


if WL_CONSUMER_KEY and WL_CONSUMER_SECRET:
    wl_consumer = oauth2.Consumer(WL_CONSUMER_KEY, WL_CONSUMER_SECRET)
else:
    wl_consumer = None


class ApiError(BaseException):
    pass


class NotAuthorizedError(BaseException):
    pass


def api_call(user, path, data=None):
    conn = OAuthConnection.get(user)
    if not conn.access:
        raise NotAuthorizedError("No WL authorization for user %s." % user)
    token = oauth2.Token(conn.token, conn.token_secret)
    client = oauth2.Client(wl_consumer, token)
    if data is not None:
        data = simplejson.dumps(data)
        data = urllib.urlencode({"data": data})
        resp, content = client.request(
                "%s%s" % (WL_API_URL, path),
                method="POST",
                body=data)
    else:
        resp, content = client.request(
                "%s%s" % (WL_API_URL, path))
    status = resp['status']

    if status == '200':
        return simplejson.loads(content)
    elif status.startswith('2'):
        return
    elif status == '401':
        raise ApiError('User not authorized for publishing.')
    else:
        raise ApiError("WL API call error")

