import re

from lxml import etree

from wiki.constants import RE_TRIM_BEGIN, RE_TRIM_END

class GradedText(object):
    _is_xml = None
    _edoc = None
    _is_wl = None
    _master = None

    ROOT = 'utwor'
    MASTERS = ['powiesc',
               'opowiadanie',
               'liryka_l',
               'liryka_lp',
               'dramat_wierszowany_l',
               'dramat_wierszowany_lp',
               'dramat_wspolczesny',
               ]
    RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'

    def __init__(self, text):
        self._text = text

    def is_xml(self):
        if self._is_xml is None:
            try:
                self._edoc = etree.fromstring(self._text)
            except etree.XMLSyntaxError:
                self._is_xml = False
            else:
                self._is_xml = True
            del self._text
        return self._is_xml

    def is_wl(self):
        if self._is_wl is None:
            if self.is_xml():
                e = self._edoc
                self._is_wl = e.tag == self.ROOT and (
                    len(e) == 1 and e[0].tag in self.MASTERS or
                    len(e) == 2 and e[0].tag == self.RDF 
                        and e[1].tag in self.MASTERS)
                if self._is_wl:
                    self._master = e[-1].tag
                del self._edoc
            else:
                self._is_wl = False
        return self._is_wl

    def master(self):
        assert self.is_wl()
        return self._master


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
        # trim the end, because there's more non-empty text
        # don't trim beginning, if `text' is the first non-empty part
        texts.append(_trim(text, trim_begin=trim_begin))
        trim_begin = True
        text = next_text
    # don't trim the end, because there's no more text coming after `text'
    # only trim beginning if it's not still the first non-empty
    texts.append(_trim(text, trim_begin=trim_begin, trim_end=False))
    return "".join(texts)
