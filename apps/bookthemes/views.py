# Create your views here.

import logging
log = logging.getLogger('platforma.bookthemes')

from django.http import HttpResponse
from django.utils import simplejson as json
from bookthemes.models import Theme

def index(request):
    themes = Theme.objects.all().values_list('name', flat=True).order_by('name')
    
    return HttpResponse(json.dumps(list(themes)), mimetype="application/json")


    