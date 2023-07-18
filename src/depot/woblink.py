import re
from django.conf import settings
import requests


def get_woblink_session(*args, **kwargs):
    session = requests.Session()
    response = session.get('https://publisher.woblink.com/login')
    token = re.search(
        r'name="_csrf_token" value="([^"]+)"',
        response.text
    ).group(1)
    data = {
        '_csrf_token': token,
    }
    data.update(settings.WOBLINK_CREDENTIALS)
    response = session.post(
        'https://publisher.woblink.com/login_check',
        data=data,
    )
    return session



