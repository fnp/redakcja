# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from catalogue.management.prompt import confirm
from catalogue.models import Book
from optparse import make_option
from datetime import date
import re
from slughifi import slughifi
from lxml import etree
from librarian import WLURI


dc_fixed = {
    'description': u'Publikacja zrealizowana w ramach projektu Cyfrowa Przyszłość (http://edukacjamedialna.edu.pl).',
    'rights': u'Creative Commons Uznanie autorstwa - Na tych samych warunkach 3.0',
    'rights_license': u'http://creativecommons.org/licenses/by-sa/3.0/',
    }

dc_namespaces = { "dc": "http://purl.org/dc/elements/1.1/" }

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--slug', dest='slug', help="Slug for master module (if empty will be generated from title)"),
        make_option('-F', '--file', dest='slugs_file', help="file with child module titles per line"),
        make_option('-t', '--title', dest='title', default='', help="title of master module"),
        make_option('-l', '--level', dest='audience', default='', help='Audience level'),
    )
    help = 'Create a master module skeleton'

    def looks_like_synthetic(self, title):
        if re.match(r"^(gim|lic)_\d[.]? ", title):
            return True
        return False

    def adopt(self, child, master, typ_, audience_, commit_args):
        fc = child[0]
        txt = fc.materialize()
        changed = False
        try:
            t = etree.fromstring(txt)
        except etree.XMLSyntaxError, e:
            print "cannot read xml in part: %s" % child.slug
            print unicode(e)
            return
        wluri = WLURI(t.xpath("//dc:identifier.url", namespaces=dc_namespaces)[0].text)
        typ = t.xpath("//dc:type", namespaces=dc_namespaces)
        if not typ:
            print "no type in DC, inserting under format" 
            fmt = t.xpath("//dc:format", namespaces=dc_namespaces)
            container = fmt.getparent()
            typ = etree.SubElement(container, etree.QName('dc', 'type'))
            container.insert(typ, container.index(fmt)+1)
            changed = True
        else:
            typ = typ[0]
        if typ.text != typ_:
            print "type is '%s', setting to '%s'" % (typ.text, typ_)
            changed = True
            typ.text = typ_
        #audience = t.xpath("//dc:audience", namespaces=dc_namespaces)[0]
        #if audience.text != audience_:
        #    print "audience is '%s', setting to '%s'" % (audience.text, audience_)
        #    changed = True
        #    audience.text = audience_
        if changed:
            print "will commit."
            fc.commit(etree.tostring(t, encoding=unicode), **commit_args)
        return wluri


    def gen_xml(self, options, synthetic_modules=[], course_modules=[], project_modules=[]):
        holder = {}
        holder['xml'] = u""
        slug = options['slug']
        if not slug:
            slug = slughifi(options['title'])

        def p(t):
            holder['xml'] += u"%s\n" % t

        def dc(k, v):
            p(u'<dc:%s xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">%s</dc:%s>' % (k, v, k))

        def t(tag, ct):
            p(u'<%s>%s</%s>' % (tag, ct, tag))

        def slug_url(slug):
            return u"http://edukacjamedialna/%s/" % slug

        p("<utwor>")
        p(u'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">')
        p(u'<rdf:Description rdf:about="http://redakcja.edukacjamedialna.edu.pl/documents/">')

        dc(u'title', options['title'])
        for s in synthetic_modules:
            dc(u'relation.hasPart', unicode(s))
        for s in course_modules:
            dc(u'relation.hasPart', unicode(s))
        for s in project_modules:
            dc(u'relation.hasPart', unicode(s))
        dc(u'publisher', u'Fundacja Nowoczesna Polska')
        #        dc(u'subject.competence', meta.get(u'Wybrana kompetencja z Katalogu', u''))
        #        dc(u'subject.curriculum', meta.get(u'Odniesienie do podstawy programowej', u''))
        ## for keyword in meta.get(u'Słowa kluczowe', u'').split(u','):
        ##     keyword = keyword.strip()
        ##     dc(u'subject', keyword)
        dc(u'description', dc_fixed['description'])
        dc(u'identifier.url', u'http://edukacjamedialna.edu.pl/%s' % slug)
        dc(u'rights', dc_fixed['rights'])
        dc(u'rights.license', dc_fixed['rights_license'])
        dc(u'format', u'xml')
        dc(u'type', u'section')
        dc(u'date', date.strftime(date.today(), "%Y-%m-%d"))
        dc(u'language', u'pol')
        p(u'</rdf:Description>')
        p(u'</rdf:RDF>')
        p(u'</utwor>')

        return holder['xml']

    def handle(self, *args, **options):
        commit_args = {
            "author_name": 'Platforma',
            "description": 'Automatycznie zaimportowane z EtherPad',
            "publishable": False,
        }

        slug = options['slug']
        if not slug:
            slug = slughifi(options['title'])
        existing = Book.objects.filter(slug=slug)

        master = None
        if existing:
            overwrite = confirm("%s exists. Overwrite?" % slug, True)
            if not overwrite:
                return
            master = existing[0]
        else:
            master = Book()
        master.slug = slug
        master.title = options['title']
        master.save()

        if len(master) == 0:
            master.add(slug, options['title'])

        synthetic_modules = []
        course_modules = []
        if 'slugs_file' in options:
            f = open(options['slugs_file'], 'r')
            try:
                titles = [l.strip() for l in f.readlines()]

                for t in titles:
                    if not t: continue
                    try:
                        b = Book.objects.get(title=t)
                    except Book.DoesNotExist:
                        print "Book for title %s does not exist" % t
                        continue
                    if self.looks_like_synthetic(t):
                        wlurl = self.adopt(b, master, 'synthetic', options['audience'], commit_args)
                        synthetic_modules.append(wlurl)
                    else:
                        wlurl = self.adopt(b, master, 'course', options['audience'], commit_args)
                        course_modules.append(wlurl)
            except Exception, e:
                print "Error getting slug list (file %s): %s" % (options['slugs_file'], e)

        print "synthetic: %s" % [unicode(z) for z in synthetic_modules]
        print "course: %s" % [unicode(z) for z in course_modules]

        xml = self.gen_xml(options, synthetic_modules, course_modules)
        c = master[0]
        print xml
        if confirm("Commit?", True):
            c.commit(xml, **commit_args)

