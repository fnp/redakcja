# -*- coding: utf-8 -*-
from copy import deepcopy
import re

from lxml import etree
from catalogue.constants import TRIM_BEGIN, TRIM_END, MASTERS

RE_TRIM_BEGIN = re.compile("^<!--%s-->$" % TRIM_BEGIN, re.M)
RE_TRIM_END = re.compile("^<!--%s-->$" % TRIM_END, re.M)


class ParseError(BaseException):
    pass


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
                a.text = ''
                del a[:]
        name = etree.tostring(name_elem, method='text', encoding='utf-8').strip()

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
        chunks[:0] = [[name, unicode(etree.tostring(copied, encoding='utf-8'), 'utf-8')]]

        parts = src.findall('.//naglowek_rozdzial')

    chunks[:0] = [[u'początek', unicode(etree.tostring(src, encoding='utf-8'), 'utf-8')]]

    for ch in chunks[1:]:
        ch[1] = add_trim_begin(ch[1])
    for ch in chunks[:-1]:
        ch[1] = add_trim_end(ch[1])

    return chunks
