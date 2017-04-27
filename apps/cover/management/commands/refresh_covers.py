# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import urllib2 as urllib
from optparse import make_option

from django.core.files.base import ContentFile
from django.core.management import BaseCommand

from cover.models import Image
from cover.utils import get_flickr_data, URLOpener, FlickrError


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--from', dest='from_id', type=int, default=1),
    )

    def handle(self, *args, **options):
        from_id = options.get('from_id', 1)
        for image in Image.objects.filter(id__gte=from_id).exclude(book=None).order_by('id'):
            print image.id
            if image.source_url and 'flickr.com' in image.source_url:
                try:
                    flickr_data = get_flickr_data(image.source_url)
                    print flickr_data
                except FlickrError as e:
                    print 'Flickr analysis failed: %s' % e
                else:
                    flickr_url = flickr_data['download_url']
                    if flickr_url != image.download_url:
                        same_url = Image.objects.filter(download_url=flickr_url)
                        if same_url:
                            print 'Download url already present in image %s' % same_url.get().id
                            continue
                    try:
                        t = URLOpener().open(flickr_data['download_url']).read()
                    except urllib.URLError:
                        print 'Broken download url'
                    except IOError:
                        print 'Connection failed'
                    else:
                        image.download_url = flickr_data['download_url']
                        image.file.save(image.file.name, ContentFile(t))
                        image.save()
