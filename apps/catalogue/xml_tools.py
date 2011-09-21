# -*- coding: utf-8 -*-
from copy import deepcopy
from functools import wraps
import re

from lxml import etree
from catalogue.constants import TRIM_BEGIN, TRIM_END, MASTERS

RE_TRIM_BEGIN = re.compile("^<!--%s-->$" % TRIM_BEGIN, re.M)
RE_TRIM_END = re.compile("^<!--%s-->$" % TRIM_END, re.M)


class ParseError(BaseException):
    pass


def obj_memoized(f):
    """
        A decorator that caches return value of object methods.
        The cache is kept with the object, in a _obj_memoized property.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_obj_memoized'):
            self._obj_memoized = {}
        key = (f.__name__,) + args + tuple(sorted(kwargs.iteritems()))
        try:
            return self._obj_memoized[key]
        except TypeError:
            return f(self, *args, **kwargs)
        except KeyError:
            self._obj_memoized[key] = f(self, *args, **kwargs)
            return self._obj_memoized[key]
    return wrapper


class GradedText(object):
    _edoc = None

    ROOT = 'utwor'
    RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'

    def __init__(self, text):
        self._text = text

    @obj_memoized
    def is_xml(self):
        """
            Determines if it's a well-formed XML.

            >>> GradedText("<a/>").is_xml()
            True
            >>> GradedText("<a>").is_xml()
            False
        """
        try:
            self._edoc = etree.fromstring(self._text)
        except etree.XMLSyntaxError:
            return False
        return True

    @obj_memoized
    def is_wl(self):
        """
            Determines if it's an XML with a <utwor> and a master tag.

            >>> GradedText("<utwor><powiesc></powiesc></utwor>").is_wl()
            True
            >>> GradedText("<a></a>").is_wl()
            False
        """
        if self.is_xml():
            e = self._edoc
            # FIXME: there could be comments
            ret = e.tag == self.ROOT and (
                len(e) == 1 and e[0].tag in MASTERS or
                len(e) == 2 and e[0].tag == self.RDF 
                    and e[1].tag in MASTERS)
            if ret:
                self._master = e[-1].tag
            del self._edoc
            return ret
        else:
            return False

    @obj_memoized
    def is_broken_wl(self):
        """
            Determines if it at least looks like broken WL file
            and not just some untagged text.

            >>> GradedText("<utwor><</utwor>").is_broken_wl()
            True
            >>> GradedText("some text").is_broken_wl()
            False
        """
        if self.is_wl():
            return True
        text = self._text.strip()
        return text.startswith('<utwor>') and text.endswith('</utwor>')

    def master(self):
        """
            Gets the master tag.

            >>> GradedText("<utwor><powiesc></powiesc></utwor>").master()
            'powiesc'
        """
        assert self.is_wl()
        return self._master

    @obj_memoized
    def has_trim_begin(self):
        return RE_TRIM_BEGIN.search(self._text)

    @obj_memoized
    def has_trim_end(self):
        return RE_TRIM_END.search(self._text)


def _trim(text, trim_begin=True, trim_end=True):
    """ 
        Cut off everything before RE_TRIM_BEGIN and after RE_TRIM_END, so
        that eg. one big XML file can be compiled from many small XML files.
    """
    if trim_begin:
        text = RE_TRIM_BEGIN.split(text, maxsplit=1)[-1]
    if trim_end:
        text = RE_TRIM_END.split(text, maxsplit=1)[0]
    return text


def compile_text(parts):
    """ 
        Compiles full text from an iterable of parts,
        trimming where applicable.
    """
    texts = []
    trim_begin = False
    text = ''
    for next_text in parts:
        if not next_text:
            continue
        if text:
            # trim the end, because there's more non-empty text
            # don't trim beginning, if `text' is the first non-empty part
            texts.append(_trim(text, trim_begin=trim_begin))
            trim_begin = True
        text = next_text
    # don't trim the end, because there's no more text coming after `text'
    # only trim beginning if it's not still the first non-empty
    texts.append(_trim(text, trim_begin=trim_begin, trim_end=False))
    return "".join(texts)


def change_master(text, master):
    """
        Changes the master tag in a WL document.
    """
    e = etree.fromstring(text)
    e[-1].tag = master
    return unicode(etree.tostring(e, encoding="utf-8"), 'utf-8')


def basic_structure(text, master):
    e = etree.fromstring('''<utwor>
<master>
<!--%s--><!--%s-->
</master>
</utwor>''' % (TRIM_BEGIN, TRIM_END))
    e[0].tag = master
    e[0][0].tail = "\n"*3 + text + "\n"*3
    return unicode(etree.tostring(e, encoding="utf-8"), 'utf-8')


def add_trim_begin(text):
    trim_tag = etree.Comment(TRIM_BEGIN)
    e = etree.fromstring(text)
    for master in e[::-1]:
        if master.tag in MASTERS:
            break
    if master.tag not in MASTERS:
        raise ParseError('No master tag found!')

    master.insert(0, trim_tag)
    trim_tag.tail = '\n\n\n' + (master.text or '')
    master.text = '\n'
    return unicode(etree.tostring(e, encoding="utf-8"), 'utf-8')


def add_trim_end(text):
    trim_tag = etree.Comment(TRIM_END)
    e = etree.fromstring(text)
    for master in e[::-1]:
        if master.tag in MASTERS:
            break
    if master.tag not in MASTERS:
        raise ParseError('No master tag found!')

    master.append(trim_tag)
    trim_tag.tail = '\n'
    prev = trim_tag.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or '') + '\n\n\n'
    else:
        master.text = (master.text or '') + '\n\n\n'
    return unicode(etree.tostring(e, encoding="utf-8"), 'utf-8')


def split_xml(text):
    """Splits text into chapters.

    All this stuff really must go somewhere else.

    """
    src = etree.fromstring(text)
    chunks = []

    splitter = u'naglowek_rozdzial'
    parts = src.findall('.//naglowek_rozdzial')
    while parts:
        # copy the document
        copied = deepcopy(src)

        element = parts[-1]

        # find the chapter's title
        name_elem = deepcopy(element)
        for tag in 'extra', 'motyw', 'pa', 'pe', 'pr', 'pt', 'uwaga':
            for a in name_elem.findall('.//' + tag):
                a.text=''
                del a[:]
        name = etree.tostring(name_elem, method='text', encoding='utf-8')

        # in the original, remove everything from the start of the last chapter
        parent = element.getparent()
        del parent[parent.index(element):]
        element, parent = parent, parent.getparent()
        while parent is not None:
            del parent[parent.index(element) + 1:]
            element, parent = parent, parent.getparent()

        # in the copy, remove everything before the last chapter
        element = copied.findall('.//naglowek_rozdzial')[-1]
        parent = element.getparent()
        while parent is not None:
            parent.text = None
            while parent[0] is not element:
                del parent[0]
            element, parent = parent, parent.getparent()
        chunks[:0] = [[name,
            unicode(etree.tostring(copied, encoding='utf-8'), 'utf-8')
            ]]

        parts = src.findall('.//naglowek_rozdzial')

    chunks[:0] = [[u'początek',
        unicode(etree.tostring(src, encoding='utf-8'), 'utf-8')
        ]]

    for ch in chunks[1:]:
        ch[1] = add_trim_begin(ch[1])
    for ch in chunks[:-1]:
        ch[1] = add_trim_end(ch[1])

    return chunks
