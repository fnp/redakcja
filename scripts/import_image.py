#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
sys.path.append('.')
sys.path.append('./apps')
sys.path.append('./lib')

from django.core.management import setup_environ
from redakcja import settings
from redakcja import localsettings

setup_environ(settings)
settings.CATALOGUE_REPO_PATH = localsettings.CATALOGUE_REPO_PATH
settings.CATALOGUE_IMAGE_REPO_PATH = localsettings.CATALOGUE_IMAGE_REPO_PATH
settings.MEDIA_ROOT = localsettings.MEDIA_ROOT
settings.STATIC_ROOT = localsettings.STATIC_ROOT


from catalogue.models import  Image
from django.core.files import File
import re
from os import path
from django.contrib.auth.models import User
from django.conf import settings



user = {
    'obj': User.objects.get(username='marcinkoziej'),
    'name': 'Marcin Koziej',
    'email': 'marcinkoziej@nowoczesnapolska.org.pl'
    }

files = sys.argv[1:]

xml = open(path.dirname(__file__)+"/image.xml").read().decode('utf-8')

for filename in files:
    dfile = File(open(filename))
    img = Image()
    name = path.splitext(path.basename(filename))[0]
    print filename, name
    try:
        old = Image.objects.get(slug=name)
        print "deleting old %s" % name
        old.delete()
    except:
        pass
    

    img.slug = name
    img.title = name
    img.image.save(filename, dfile)

    img.save()
    img.commit(xml, author=user['obj'], author_name=user['name'], author_email=user['email'])


    
