# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import urllib2 as urllib
from django.core.files.base import ContentFile
from django.core.management import BaseCommand

from cover.models import Image
from cover.utils import get_flickr_data, URLOpener, FlickrError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--from', dest='from_id', type=int, default=1)

    def handle(self, *args, **options):
        from_id = options.get('from_id', 1)
        images = Image.objects.filter(id__gte=from_id).exclude(book=None).order_by('id')
        images = images.filter(source_url__contains='flickr.com').exclude(download_url__endswith='_o.jpg')
        for image in images:
            print(image.id)
            try:
                flickr_data = get_flickr_data(image.source_url)
                print(flickr_data)
            except FlickrError as e:
                print('Flickr analysis failed: %s' % e)
            else:
                flickr_url = flickr_data['download_url']
                if flickr_url != image.download_url:
                    same_url = Image.objects.filter(download_url=flickr_url)
                    if same_url:
                        print('Download url already present in image %s' % same_url.get().id)
                        continue
                try:
                    t = URLOpener().open(flickr_url).read()
                except urllib.URLError:
                    print('Broken download url')
                except IOError:
                    print('Connection failed')
                else:
                    image.download_url = flickr_url
                    image.file.save(image.file.name, ContentFile(t))
                    image.save()
