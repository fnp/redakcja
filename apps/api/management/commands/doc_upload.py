#!/usr/bin/env python
# -*- conding: utf-8 -*-
__author__="lreqc"
__date__ ="$2009-09-08 14:31:26$"

from django.core.management.base import BaseCommand
from django.utils import simplejson as json
from django.test.client import Client
from django.core.urlresolvers import reverse

from optparse import make_option

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('-u', '--user', action='store', dest='username'),
        make_option('-p', '--password', action='store', dest='password'),
        make_option('-d', '--dublin-core', action='store_true', dest='dc'),
    )
    
    def handle(self, *args, **options):
        client = Client()
        if not options['username'] or not options['password']:
            raise CommandError("You must provide login data")

        client.login(username=options['username'], \
            password=options['password'])

        print options['username'], options['password']
        
        filename = args[0]
        bookname = args[1]

        print "Uploading '%s' as document '%s'" % (filename, bookname)
        print "Wth DC template" if options['dc'] else ""

        print client.post( reverse("document_list_view"),\
        {
            'bookname': bookname,
            'ocr_file': open(filename),
            'generate_dc': options['dc'] } )
                  
