# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import re
from urllib import FancyURLopener

from django.contrib.sites.models import Site


class URLOpener(FancyURLopener):
    @property
    def version(self):
        return 'FNP Redakcja (http://%s)' % Site.objects.get_current()


class FlickrError(Exception):
    pass


def get_flickr_data(url):
    m = re.match(r'(https?://)?(www\.|secure\.)?flickr\.com/photos/(?P<author>[^/]+)/(?P<img>\d+)/?', url)
    if not m:
        raise FlickrError("It doesn't look like Flickr URL.")
    author_slug, img_id = m.group('author'), m.group('img')
    base_url = "https://www.flickr.com/photos/%s/%s/" % (author_slug, img_id)
    try:
        html = URLOpener().open(url).read().decode('utf-8')
    except IOError:
        raise FlickrError('Error reading page')
    match = re.search(r'<a href="([^"]*)"[^>]* rel="license ', html)
    if not match:
        raise FlickrError('License not found.')
    else:
        license_url = match.group(1)
        re_license = re.compile(r'https?://creativecommons.org/licenses/([^/]*)/([^/]*)/.*')
        m = re_license.match(license_url)
        if not m:
            raise FlickrError('License does not look like CC: %s' % license_url)
        license_name = 'CC %s %s' % (m.group(1).upper(), m.group(2))
    m = re.search(r'<a[^>]* class="owner-name [^>]*>([^<]*)<', html)
    if m:
        author = "%s@Flickr" % m.group(1)
    else:
        raise FlickrError('Error reading author name.')
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if not m:
        raise FlickrError('Error reading image title.')
    title = m.group(1).strip()
    m = re.search(r'modelExport: (\{.*\})', html)
    try:
        assert m
        download_url = 'https:' + json.loads(m.group(1))['main']['photo-models'][0]['sizes']['o']['url']
    except (AssertionError, ValueError, IndexError, KeyError):
        raise FlickrError('Error reading image URL.')
    return {
        'source_url': base_url,
        'license_url': license_url,
        'license_name': license_name,
        'author': author,
        'title': title,
        'download_url': download_url,
    }
