# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""
   Abstraction over API for wolnelektury.pl
"""
import urllib2
import functools
import json
import logging
logger = logging.getLogger("fnp.lib.wlapi")


class APICallException(Exception):

    def __init__(self, cause=None):
        super(Exception, self).__init__()
        self.cause = cause

    def __unicode__(self):
        return u"%s, cause: %s" % (type(self).__name__, repr(self.cause))

    def __str__(self):
        return self.__unicode__().encode('utf-8')


def api_call(path, format="json"):
    def wrapper(func):

        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            generator = func(self, *args, **kwargs)

            data = generator.next()

            # prepare request
            rq = urllib2.Request(self.base_url + path + ".json")

            # will send POST when there is data, GET otherwise
            if data is not None:
                rq.add_data(json.dumps(data))
                rq.add_header("Content-Type", "application/json")

            try:
                anwser = json.load(self.opener.open(rq))
                try:
                    return generator.send(anwser)
                except StopIteration:
                    # by default, just return the anwser as a shorthand
                    return anwser
            except urllib2.HTTPError, error:
                return self._http_error(error)
            except Exception, error:
                return self._error(error)
        return wrapped

    return wrapper


class WLAPI(object):

    def __init__(self, **config_dict):
        self.base_url = config_dict['URL']
        self.auth_realm = config_dict['AUTH_REALM']
        self.auth_user = config_dict['AUTH_USER']

        digest_handler = urllib2.HTTPDigestAuthHandler()
        digest_handler.add_password(
                    realm=self.auth_realm, uri=self.base_url,
                    user=self.auth_user, passwd=config_dict['AUTH_PASSWD'])

        basic_handler = urllib2.HTTPBasicAuthHandler()
        basic_handler.add_password(
                    realm=self.auth_realm, uri=self.base_url,
                    user=self.auth_user, passwd=config_dict['AUTH_PASSWD'])

        self.opener = urllib2.build_opener(digest_handler, basic_handler)

    def _http_error(self, error):
        message = error.read()
        logger.debug("HTTP ERROR: %s", message)
        return self._error(message)

    def _error(self, error):
        raise APICallException(error)

    @api_call("books")
    def list_books(self):
        yield

    @api_call("books")
    def publish_book(self, document):
        yield {"text": document.text, "compressed": False}
