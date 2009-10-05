#!/usr/bin/env python
# -*- conding: utf-8 -*-
__author__="lreqc"
__date__ ="$2009-09-08 14:31:26$"

from django.core.management.base import NoArgsCommand

# from optparse import make_option

class Command(NoArgsCommand):
      
    def handle(self, *args, **options):
        client = Client()
        if not options['username'] or not options['password']:
            raise CommandError("You must provide login data")

        client.login(username=options['username'], \
            password=options['password'])

        print options['username'], options['password']

        docid = args[0]

        url = reverse("document_view", args=[docid])
        print "Quering %s" % url
        resp = client.get(url)

        result = json.loads(resp.content)
        print result

        print "Current revision for '%s': %s" % (docid, result['user_revision'])
        url = reverse("docmerge_view", args=[docid])
        print "Sending POST to %s" % url
        resp = client.post(url, {
            'type': 'share',
            'target_revision': result['user_revision'],
            'message': 'Sharing.. :)'          
        })

        print resp.status_code, resp.content
