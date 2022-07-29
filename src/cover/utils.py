# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import csv
from io import StringIO
import json
import re
from urllib.request import FancyURLopener
from django.conf import settings
import requests
from wikidata.client import Client
from catalogue.constants import WIKIDATA


class URLOpener(FancyURLopener):
    @property
    def version(self):
        return 'FNP Redakcja'


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
            re_pd = re.compile(r'https?://creativecommons.org/publicdomain/([^/]*)/([^/]*)/.*')
            m = re_pd.match(license_url)
            if not m:
                raise FlickrError('License does not look like CC: %s' % license_url)
            if m.group(1).lower() == 'zero':
                license_name = 'Public domain (CC0 %s)' % m.group(2)
            else:
                license_name = 'Public domain'
        else:
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


def get_wikimedia_data(url):
    file_name = url.rsplit('/', 1)[-1].rsplit(':', 1)[-1]
    d = json.loads(URLOpener().open('https://commons.wikimedia.org/w/api.php?action=query&titles=File:{}&prop=imageinfo&iiprop=url|user|extmetadata&iimetadataversion=latest&format=json'.format(file_name)).read().decode('utf-8'))

    d = list(d['query']['pages'].values())[0]['imageinfo'][0]
    ext = d['extmetadata']

    meta = {
        'title': ext['ObjectName']['value'],
        'author': d['user'],
        'source_url': d['descriptionurl'],
        'download_url': d['url'],
        'license_url': ext.get('LicenseUrl', {}).get('value', ''),
        'license_name': ext['LicenseShortName']['value'],
    }

    # There are Wikidata links in ObjectName sametimes. Let's use it.
    wikidata_match = re.search(r'wikidata\.org/wiki/(Q\d+)', meta['title'])
    if wikidata_match is not None:
        qitem = wikidata_match.group(1)
        client = Client()
        entity = client.get(qitem)
        meta['title'] = entity.label.get('pl', str(entity.label))
        author = entity.get(client.get(WIKIDATA.CREATOR))
        meta['author'] = author.label.get('pl', str(author.label))

    if meta['license_name'] == 'Public domain':
        meta['license_name'] = 'domena publiczna'
        meta['license_url'] = 'https://pl.wikipedia.org/wiki/Domena_publiczna'


    return meta


def get_mnw_data(url):
    nr = url.rsplit('/', 1)[-1]
    d = list(
        csv.DictReader(
            StringIO(
                URLOpener().open(
                    'https://cyfrowe-api.mnw.art.pl/api/object/{}/csv'.format(nr)
                ).read().decode('utf-8')
            )
        )
    )[0]

    authors = []
    i = 1
    while f'twórca/wytwórnia {i}' in d:
        authors.append(d[f'twórca/wytwórnia {i}'])
        i += 1

    license_url = ''
    license_name = d['klasyfikacja praw autorskich 1']
    if license_name == 'DOMENA PUBLICZNA':
        license_name = 'domena publiczna'
        license_url = 'https://pl.wikipedia.org/wiki/Domena_publiczna'
        
    return {
        'title': d['nazwa/tytuł'],
        'author': ', '.join(authors),
        'source_url': url,
        'download_url': 'https://cyfrowe-cdn.mnw.art.pl/upload/multimedia/{}.{}'.format(
            d['ścieżka wizerunku'],
            d['rozszerzenie pliku wizerunku'],
        ),
        'license_url': license_url,
        'license_name': license_name,
    }

def get_rawpixel_data(url):
    photo_id = re.search(r'/(\d+)/', url).group(1)

    s = requests.Session()
    cookies = settings.RAWPIXEL_SESSION

    token = s.post(
            'https://www.rawpixel.com/api/v1/user/session',
            cookies=cookies
            ).json()['token']

    h = {'X-CSRF-Token': token, 'Accept': 'application/json'}

    data = s.get(
        f'https://www.rawpixel.com/api/v1/image/data/{photo_id}',
        headers=h, cookies=cookies).json()
    download_url = s.post(
        f'https://www.rawpixel.com/api/v1/image/download/{photo_id}/original',
        headers=h, cookies=cookies
    ).json()['downloadUrl']

    title = data['metadata']['title'].rsplit('|', 1)[0].strip()

    return {
        'title': title,
        'author': ', '.join(data['metadata']['artist_names']),
        'source_url': data['url'],
        'download_url': download_url,
        'license_url': data['metadata']['licenseUrl'],
        'license_name': data['metadata']['license'],
    }


def get_import_data(url):
    if re.match(r'(https?://)?(www\.|secure\.)?flickr\.com/', url):
        return get_flickr_data(url)
    if re.match(r'(https?://)?(commons|upload)\.wikimedia\.org/', url):
        return get_wikimedia_data(url)
    if re.match(r'(https?://)?cyfrowe\.mnw\.art\.pl/', url):
        return get_mnw_data(url)
    if re.match(r'(https?://)?www\.rawpixel\.com/', url):
        return get_rawpixel_data(url)
