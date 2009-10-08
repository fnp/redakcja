# Create your views here.

from django.http import HttpResponse
from librarian import html
from lxml import etree
from StringIO import StringIO
import re

LINE_SWAP_EXPR = re.compile(r'/\s', re.MULTILINE | re.UNICODE);

def render(request):    
    style_filename = html.get_stylesheet('partial')

    data = request.POST['fragment']
    path = request.POST['part']

    base, me = path.rsplit('/', 1)
    match = re.match(r'([^\[]+)\[(\d+)\]', me)
    tag, pos = match.groups()

    print "Redner:", path, base, tag, pos

    style = etree.parse(style_filename)

    data = LINE_SWAP_EXPR.sub(u'<br />\n', data)
    doc = etree.parse( StringIO(data) )

    opts = {
        'with-paths': 'boolean(1)',
        'base-path': "'%s'" % base,
        'base-offset': pos,
    }

    print opts
    
    result = doc.xslt(style, **opts)

    print result
    
    return HttpResponse(
        etree.tostring(result, encoding=unicode, pretty_print=True) )