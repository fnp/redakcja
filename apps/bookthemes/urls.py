__author__="lreqc"
__date__ ="$2009-09-17 16:16:54$"

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'bookthemes.views.index'),
)

