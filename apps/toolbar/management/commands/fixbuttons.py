# -*- conding: utf-8
__author__="lreqc"
__date__ ="$2009-09-08 14:31:26$"
from django.core.management.base import NoArgsCommand
from toolbar.models import Button
import json
import re

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        buttons = Button.objects.all()
        for b in buttons:
            params = b.params;
            try:
                v = json.loads(b.params)
               
            except ValueError, e:
                print 'On button %s: ' % b.label, b.params
                print e
                # try to fix the bad json
                
                # cut the parenthis
                if params[0] == u'(':
                    params = params[1:]
                if params[-1] == u')':
                    params = params[:-1]

                v = json.loads(re.sub(u'([\\w-]+)\\s*:', u'"\\1": ', params).encode('utf-8'))
            b.params = json.dumps(v)
            b.save()



    