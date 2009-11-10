#!/usr/bin/env python

import urllib

from lxml import html

URL = "http://redmine.nowoczesnapolska.org.pl/projects/wl-publikacje/wiki/Spis_motyw%C3%B3w_i_temat%C3%B3w_literackich?format=html"
doc = html.parse(URL)


for element in doc.xpath('//td'):
    print "- model: bookthemes.theme"
    print "  pk:", element.text_content().strip().encode('utf-8')
    print '  fields: {description: ""}'
