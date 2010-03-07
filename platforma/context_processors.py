# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-09-03 08:34:10$"

def settings(request):
    from django.conf import settings
    return {'MEDIA_URL': settings.MEDIA_URL, 
            'STATIC_URL': settings.STATIC_URL,
            'REDMINE_URL': settings.REDMINE_URL }


