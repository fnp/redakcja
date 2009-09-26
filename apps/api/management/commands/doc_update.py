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
    )
    
    def handle(self, *args, **options):
        client = Client()
        if not options['username'] or not options['password']:
            raise CommandError("You must provide login data")

        client.login(username=options['username'], \
            password=options['password'])

        print options['username'], options['password']

        filename = args[0]
        docid = args[1]

        url = reverse("document_view", args=[docid])
        print "Quering %s" % url
        resp = client.get(url)

        result = json.loads(resp.content)
        print result

        print "Current revision for '%s': %s" % (docid, result['user_revision'])
        url = reverse("doctext_view", args=[ docid, result['user_revision'] ])
        print "Sending PUT to %s" % url

        resp = client.put(url, {
            'contents': open(filename).read(),
            'message': options['message'] or ''
            
        })

        print resp.status_code, resp.content
