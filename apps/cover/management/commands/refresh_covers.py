# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import urllib2 as urllib

from django.core.files.base import ContentFile
from django.core.management.base import NoArgsCommand

from cover.models import Image
from cover.utils import get_flickr_data, URLOpener, FlickrError


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for image in Image.objects.exclude(book=None).order_by('id'):
            print image.id
            if 'flickr.com' in image.source_url:
                try:
                    flickr_data = get_flickr_data(image.source_url)
                except FlickrError as e:
                    print 'Flickr analysis failed: %s' % e
                else:
                    try:
                        t = URLOpener().open(image.download_url).read()
                    except urllib.URLError:
                        print 'Broken download url'
                    except IOError:
                        print 'Connection failed'
                    else:
                        image.download_url = flickr_data['download_url']
                        image.file.save(image.file.name, ContentFile(t))
                        image.save()
