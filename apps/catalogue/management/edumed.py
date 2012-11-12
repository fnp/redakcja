# EduMed auto-tagger
# -*- coding: utf-8 -*-
import re
from slughifi import slughifi


class Tagger:
    def __init__(self, state, lines):
        self.state = state
        self.lines = lines

    def spawn(self, cls):
        return cls(self.state, self.lines)

    def line(self, position):
        return self.lines[position]

    empty_line = re.compile(r"\s+")
    
    def skip_empty(self, position):
        while self.line(position) == "" or \
            self.empty_line.match(self.line(position)):
            position += 1
        return position

    def tag(self, position):
        """
Return None -- means that we can't tag it in any way
        """
        return None

    def wrap(self, tagname, content):
        return u"<%s>%s</%s>" % (tagname, content, tagname)


class Section(Tagger):
    looks_like = re.compile(r"^[IVX]+[.]\s+(.*)$")

    def tag(self, pos):
        pos2 = self.skip_empty(pos)
        pos = pos2
        m = self.looks_like.match(self.line(pos))
        if m:
            self.title = m.groups()[0]
            return pos + 1

    def __unicode__(self):
        return self.wrap("naglowek_rozdzial", self.title)


class Meta(Tagger):
    looks_like = re.compile(r"([^:]+): (.*)", re.UNICODE)

    def tag(self, pos):
        pos = self.skip_empty(pos)
        m = self.looks_like.match(self.line(pos))
        if m:
            k = m.groups()[0]
            v = m.groups()[1]
            m = self.state.get('meta', {})
            m[k] = v
            self.state['meta'] = m
            return pos + 1


class Informacje(Tagger):
    def tag(self, pos):
        self.title = self.spawn(Section)
        self.meta = []
        pos = self.title.tag(pos)
        if pos is None: return

            # collect meta
        while True:
            pos = self.skip_empty(pos)
            meta = self.spawn(Meta)
            pos2 = meta.tag(pos)
            if pos2 is None: break
            self.meta.append(meta)
            pos = pos2

        return pos


class List(Tagger):
    def tag(self, pos):
        self.items = []
        while True:
            l = self.line(pos)
            if l and l[0] in ('-', '*'):
                self.items.append(l[1:].strip())
                pos += 1
            else:
                break
        if self.items:
            return pos

    def __unicode__(self):
        s = "<lista>\n"
        for i in self.items:
            s += "<punkt>%s</punkt>\n" % i
        s += "</lista>\n"
        return s


class Paragraph(Tagger):
    remove_this = [
        re.compile(r"[\s]*opis zawartości[\s]*", re.I),
        re.compile(r"^[\s]*$")
        ]
    podrozdzial = [
        re.compile(r"[\s]*(przebieg zajęć|opcje dodatkowe)[\s]*", re.I),
        ]
    def tag(self, pos):
        self.line = self.lines[pos]
        self.ignore = False
        self.is_podrozdzial = False
        
        for x in self.remove_this:
            if x.match(self.line):
                self.ignore = True
                
        for x in self.podrozdzial:
            if x.match(self.line):
                self.is_podrozdzial = True
                
        return pos + 1

    def __unicode__(self):
        if not self.ignore:
            if self.is_podrozdzial:
                tag = 'naglowek_podrozdzial'
            else:
                tag = 'akap'
            return u"<%s>%s</%s>" % (tag, self.line, tag)
        else:
            return u''


class Container:
    def __init__(self, tag_name, *elems):
        self.tag_name = tag_name
        self.elems = elems

    def __unicode__(self):
        s = u"<%s>" % self.tag_name
        add_nl = False
        for e in self.elems:
            if isinstance(e, (str, unicode)):
                s += unicode(e)
            else:
                s += "\n  " + unicode(e)
                add_nl = True

        if add_nl: s += "\n"
        s += u"</%s>" % self.tag_name
        return s


def eatany(pos, *taggers):
    try:
        for t in list(taggers):
            p = t.tag(pos)
            if p:
                return (t, p)
    except IndexError:
        pass
    return (None, pos)


def eatseq(pos, *taggers):
    good = []
    taggers = list(taggers[:])
    try:
        while len(taggers):
            p = taggers[0].tag(pos)
            if p is None:
                return (tuple(good), pos)
            good.append(taggers.pop(0))
            # print "%d -> %d" % (pos, p)
            pos = p

    except IndexError:
        print "Got index error for pos=%d" % pos
    return (tuple(good), pos)


def tagger(text):
    """
tagger(text) function name and signature is a contract.
returns auto-tagged text
    """
    if not isinstance(text, unicode):
        text = unicode(text.decode('utf-8'))
    lines = text.split("\n")
    pos = 0
    content = []
    state = {}
    info = Informacje(state, lines)
    
    ((info,), pos) = eatseq(pos, info)

    # print "[i] %d. %s" % (pos, lines[pos])

    content.append(info)

    while True:
        x, pos = eatany(pos, info.spawn(Section),
                        info.spawn(List), info.spawn(Paragraph))

        if x is not None:
            content.append(x)
        else:
            content.append(lines[pos])
            pos += 1
            if pos >= len(lines):
                break

    return toxml(content)

dc_fixed = {
    'description': u'Publikacja zrealizowana w ramach projektu Cyfrowa Przyszłość (http://cyfrowaprzyszlosc.pl).',
    'relation':  u'moduły powiązane linki',
    'description.material': u'linki do załączników',
    'rights': u'Creative Commons Uznanie autorstwa - Na tych samych warunkach 3.0',
    }


def mark_activities(content):
    i = 0
    tl = len(content)
    is_przebieg = re.compile(r"[\s]*przebieg zaj..[\s]*", re.I)
    #    import pdb; pdb.set_trace()
    is_next_section = re.compile(r"^[IVX]+[.]? ")
    is_activity = re.compile(r"^[0-9]+[.]? (.+)")

    is_activity_tools = re.compile(r"^pomoce:[\s]*(.+)")
    is_activity_work = re.compile(r"^forma pracy:[\s]*(.+)")
    is_activity_time = re.compile(r"^czas:[\s]*([\d]+).*")
    activity_props = {
        'pomoce': is_activity_tools,
        'forma': is_activity_work,
        'czas': is_activity_time
        }
    activities = []

    in_activities = False
    ab = -1
    ae = -1
    while True:
        e = content[i]
        if isinstance(e, Paragraph):
            if not in_activities and \
                is_przebieg.match(e.line):
                in_activities = True

            if in_activities and \
                is_next_section.match(e.line):
                in_activities = False
            if in_activities:
                m = is_activity.match(e.line)
                if m:
                    e.line = m.groups()[0]
                    ab = i
                if is_activity_time.match(e.line):
                    ae = i + 1
                    activities.append((ab, ae))
        i += 1
        if i >= tl: break

    activities.reverse()
    for ab, ae in activities:
        act_len = ae - ab
        info_start = ae

        act_els = []
        act_els.append(Container("opis", content[ab]))
        for i in range(ab, ae):
            e = content[i]
            if isinstance(e, Paragraph):
                for prop, pattern in activity_props.items():
                    m = pattern.match(e.line)
                    if m:
                        act_els.append(Container(prop, m.groups()[0]))
                        if info_start > i: info_start = i
        act_els.insert(1, Container('wskazowki',
                                    *content[ab + 1:info_start]))
        content[ab:ae] = [Container('aktywnosc', *act_els)]
    return content


def mark_dictionary(content):
    db = -1
    de = -1
    i = 0
    is_dictionary = re.compile(r"[\s]*s.owniczek[\s]*", re.I)
    is_dictentry = re.compile(r"([^-]+) - (.+)")
    slowniczek = []
    while i < len(content):
        e = content[i]
        if isinstance(e, Section):
            if is_dictionary.match(e.title):
                db = i + 1
            elif db >= 1:
                de = i
                content[db:de] = [Container('slowniczek', *slowniczek)]
        elif db >= 0:
            if isinstance(e, Paragraph):
                m = is_dictentry.match(e.line)
                if m:
                    slowniczek.append(Container('definiendum', m.groups()[0]))
                    slowniczek.append(Container('definiens', m.groups()[1]))
                else:
                    slowniczek.append(e)
        i += 1

    return content


def toxml(content):
    content = mark_activities(content)
    content = mark_dictionary(content)
    info = content.pop(0)

    state = info.state
    meta = state['meta']
    slug = slughifi(meta.get(u'Tytuł modułu', ''))
    holder = {}
    holder['xml'] = u""

    def p(t):
        holder['xml'] += u"%s\n" % t

    def dc(k, v):
        p(u'<dc:%s xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">%s</dc:%s>' % (k, v, k))

    def t(tag, ct):
        p(u'<%s>%s</%s>' % (tag, ct, tag))

    def a(ct):
        if ct:
            t(u'akap', ct)

    p("<utwor>")
    p(u'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">')
    p(u'<rdf:Description rdf:about="http://redakcja.cyfrowaprzyszlosc.pl/documents/">')
    authors = map(unicode.strip, meta[u'Autorzy'].split(u','))
    for author in authors:
        names = author.split(u' ')
        lastname = names.pop()
        names.insert(0, lastname + ",")
        author = u' '.join(names)
        dc(u'creator', author)
    dc(u'title', meta.get(u'Tytuł modułu', u''))
    dc(u'relation.isPartOf', meta.get(u'Dział', u''))
    dc(u'publisher', u'Fundacja Nowoczesna Polska')
    dc(u'subject.competence', meta.get(u'Wybrana kompetencja z Katalogu', u''))
    dc(u'subject.curriculum', meta.get(u'Odniesienie do podstawy programowej', u''))
    for keyword in meta.get(u'Słowa kluczowe', u'').split(u','):
        keyword = keyword.strip()
        dc(u'subject', keyword)
    dc(u'description', dc_fixed['description'])
    dc(u'description.material', dc_fixed['description.material'])
    dc(u'relation', dc_fixed['relation'])
    dc(u'identifier.url', u'http://cyfrowaprzyszlosc.pl/%s' % slug)
    dc(u'rights', dc_fixed['rights'])
    dc(u'rights.license', u'http://creativecommons.org/licenses/by-sa/3.0/')
    dc(u'format', u'xml')
    dc(u'type', u'text')
    dc(u'date', u'2012-11-09')  # TODO
    dc(u'audience', meta.get(u'Poziom edukacyjny', u''))
    dc(u'language', u'pol')
    p(u'</rdf:Description>')
    p(u'</rdf:RDF>')

    p(u'<powiesc>')
    t(u'nazwa_utworu', meta.get(u'Tytuł modułu', u''))
    p(u'<nota>')
    a(u'Numer porządkowy: %s' % meta.get(u'Numer porządkowy', u''))
    p(u'</nota>')

    p(unicode(info.title))
    for elm in content:
        if isinstance(elm, unicode) or isinstance(elm, str):
            a(elm)
            continue
        p(unicode(elm))

    p(u'</powiesc>')
    p(u'</utwor>')

    return holder['xml']


# TODO / TBD
# ogarnąć podrozdziały
#  Przebieg zajęć
#  opcje dodatkowe
# usunąć 'opis zawartości'
# akapit łączony?
