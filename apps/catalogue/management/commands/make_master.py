# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from catalogue.management.prompt import confirm
from catalogue.models import Book
from optparse import make_option
from datetime import date
import re
from slughifi import slughifi


dc_fixed = {
    'description': u'Publikacja zrealizowana w ramach projektu Cyfrowa Przyszłość (http://edukacjamedialna.edu.pl).',
    'rights': u'Creative Commons Uznanie autorstwa - Na tych samych warunkach 3.0',
    'rights_license': u'http://creativecommons.org/licenses/by-sa/3.0/',
    }


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--slug', dest='slug', help="Slug for master module"),
        make_option('-F', '--file', dest='slugs_file', help="file with child module slugs per line"),
        make_option('-t', '--title', dest='title', default='', help="title of master module"),
        make_option('-l', '--level', dest='audience', default='', help='Audience level'),
    )
    help = 'Create a master module skeleton'

    def looks_like_synthetic(self, title):
        if re.match(r"^(gim|lic)_\d[.]? ", title):
            return True
        return False

    def gen_xml(self, options, synthetic_modules=[], course_modules=[], project_modules=[]):
        holder = {}
        holder['xml'] = u""

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
        for slug in synthetic_modules:
            dc(u'relation.hasChild.synthetic', slug_url(slug))
        for slug in course_modules:
            dc(u'relation.hasChild.course', slug_url(slug))
        for slug in project_modules:
            dc(u'relation.hasChild.project', slug_url(slug))
        dc(u'publisher', u'Fundacja Nowoczesna Polska')
        #        dc(u'subject.competence', meta.get(u'Wybrana kompetencja z Katalogu', u''))
        #        dc(u'subject.curriculum', meta.get(u'Odniesienie do podstawy programowej', u''))
        ## for keyword in meta.get(u'Słowa kluczowe', u'').split(u','):
        ##     keyword = keyword.strip()
        ##     dc(u'subject', keyword)
        dc(u'description', dc_fixed['description'])
        dc(u'identifier.url', u'http://edukacjamedialna.edu.pl/%s' % options['slug'])
        dc(u'rights', dc_fixed['rights'])
        dc(u'rights.license', dc_fixed['rights_license'])
        dc(u'format', u'synthetic, course, project')
        dc(u'type', u'text')
        dc(u'date', date.strftime(date.today(), "%Y-%m-%d"))
        dc(u'audience', options['audience'])
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
                        synthetic_modules.append(b.slug)
                    else:
                        course_modules.append(b.slug)
            except Exception, e:
                print "Error getting slug list (file %s): %s" % (options['slugs_file'], e)

        print "synthetic: %s" % synthetic_modules
        print "course: %s" % course_modules

        xml = self.gen_xml(options, synthetic_modules, course_modules)
        c = master[0]
        print xml
        if confirm("Commit?", True):
            c.commit(xml, **commit_args)

