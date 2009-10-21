# Create your views here.

import logging
log = logging.getLogger('platforma.render')

from django.http import HttpResponse
import librarian
from librarian import html
from lxml import etree
from StringIO import StringIO
import re

LINE_SWAP_EXPR = re.compile(r'/\s', re.MULTILINE | re.UNICODE);

def render(request):    
    style_filename = html.get_stylesheet('partial')

    data = request.POST['fragment']
    path = request.POST['chunk']

    base, me = path.rsplit('/', 1)
    match = re.match(r'([^\[]+)\[(\d+)\]', me)
    tag, pos = match.groups()   

    style = etree.parse(style_filename)

    data = u'<chunk>%s</chunk>' % LINE_SWAP_EXPR.sub(u'<br />\n', data)
    log.info(data)    
    doc = etree.parse( StringIO(data) )

    opts = {
        'with-paths': 'boolean(1)',
        'base-path': "'%s'" % base,
        'base-offset': pos,
    }

    result = doc.xslt(style, **opts)
    log.info( str(doc), str(result) )
        
    return HttpResponse( librarian.serialize_children(result.getroot()) )