"""CAS authentication backend"""

from urllib import urlencode, urlopen
from urlparse import urljoin
from django.conf import settings
from django_cas.models import User

__all__ = ['CASBackend']


def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns (username, None) on success and (None, None) on failure.
    """

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'validate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip(), None
        else:
            return None, None
    finally:
        page.close()


def _verify_cas2(ticket, service):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns (username, attr_dict) on success and (None, None) on failure.
    """

    try:
        from lxml import etree as ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'serviceValidate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            attrs = {}
            for tag in tree[0][1:]:
                attrs[tag.tag] = tag.text
            return tree[0][0].text, attrs
        else:
            return None, None
    except:
        import traceback
        traceback.print_exc()
        print "****", url
        print response
        print "****"
    finally:
        page.close()


_PROTOCOLS = {'1': _verify_cas1, '2': _verify_cas2}

if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


class CASBackend(object):
    """CAS authentication backend"""

    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""

        username, attrs = _verify(ticket, service)
        if not username:
            return None

        user_attrs = {}
        if hasattr(settings, 'CAS_USER_ATTRS_MAP'):
            attr_map = settings.CAS_USER_ATTRS_MAP
            for k, v in attrs.items():
                if k in attr_map:
                    user_attrs[attr_map[k]] = v # unicode(v, 'utf-8')

        try:
            user = User.objects.get(username__iexact=username)
            # update user info
            changed = False
            for k, v in user_attrs.items():
                if getattr(user, k) != v:
                    setattr(user, k, v)
                    changed = True
            if changed:
                user.save()
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            for k, v in user_attrs.items():
                setattr(user, k, v)
            user.first_name = attrs.get('firstname', '')
            user.last_name = attrs.get('lastname', '')
            user.save()
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
