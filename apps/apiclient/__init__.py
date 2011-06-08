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
    # what if not verified?
    conn = OAuthConnection.get(user)
    if not conn.access:
        raise NotAuthorizedError("No WL authorization for user %s." % user)
    token = oauth2.Token(conn.token, conn.token_secret)
    client = oauth2.Client(wl_consumer, token)
    if data is not None:
        resp, content = client.request(
                "%s%s.json" % (WL_API_URL, path),
                method="POST",
                body=urllib.urlencode(data))
    else:
        resp, content = client.request(
                "%s%s.json" % (WL_API_URL, path))
    status = resp['status']
    if status == '200':
        return simplejson.loads(content)
    elif status.startswith('2'):
        return
    else:
        raise ApiError("WL API call error")

