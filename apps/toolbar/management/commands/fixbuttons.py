# -*- conding: utf-8
__author__="lreqc"
__date__ ="$2009-09-08 14:31:26$"
from django.core.management.base import NoArgsCommand
from toolbar.models import Button
from django.utils import simplejson as json
import re

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        buttons = Button.objects.all()
        print "Validating parameters... "
        for b in buttons:
            params = b.params;
            try:
                v = json.loads(b.params)               
            except ValueError, e:
                print 'Trying to fix button "%s" ...' % b.slug
                if params[0] == u'(':
                    params = params[1:]
                if params[-1] == u')':
                    params = params[:-1]
                try:
                    v = son.loads(re.sub(u'([\\w-]+)\\s*:', u'"\\1": ', params).encode('utf-8'))
                except ValueError, e:
                    print "Unable to fix '%s' " % b.params
                    print "Try to fix this button manually and rerun the script."
                    return False

            # resave
            b.params = json.dumps(v)
            b.save()

        print "Merge duplicate buttons (if any)..."
        hash = {}
        for b in buttons:
            if b.slug not in hash:
                hash[b.slug] = b
                continue
                
            # duplicate button
            print "Found duplicate of '%s'" % b.slug
            a = hash[b.slug]

            remove_duplicate = True
            if a.params != b.params:
                print "Conflicting params for duplicate of '%s'." % b.slug
                print "Groups will be joined, but won't remove duplicates."
                remove_duplicate = False

            for g in b.group.all():
                a.group.add(g)

            b.group.clear()

            a.save()
            b.delete()
