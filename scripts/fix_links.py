#!/usr/bin/env python
import argparse
import os
import sys
import re

from librarian.parser import WLDocument

_BASE = ur"""http://wiki.wolnepodreczniki.pl/(?:index.php\?title=)?Lektury(?::|/)"""

ABOUT_PATTERNS = (
    ur"""%s(?P<title>[^/]+)/?$""" % _BASE,
    ur"""%s(?P<author>[^/]+)/(?P<title>[^/]+)/?$""" % _BASE,
    ur"""%s(?P<author>[^/]+)/(?P<collection>[^/]+)/(?P<title>[^/]+)/?$""" % _BASE,
    ur"""%s(?P<author>[^/]+)/(?P<collection>[^/]+)/(?P<part>[^/]+)/(?P<title>[^/]+)/?$""" % _BASE,
)

def compile_patterns(patterns):
    for p in patterns:
        yield re.compile(p, re.UNICODE)

def match_first(text, patterns):
    for pattern in patterns:
        m = pattern.match(text)
        if m is not None:
            return m.groups()
    return False


class Task(object):

    def __init__(self):
        self.documents = set()
        self.invalid = set()
        self.unrecognized = {}
        self.duplicates = {}
        self.about_patterns = list(compile_patterns(ABOUT_PATTERNS))

        assert match_first("""http://wiki.wolnepodreczniki.pl/index.php?title=Lektury:Mickiewicz/%C5%9Amier%C4%87_Pu%C5%82kownika/""", self.about_patterns)
        assert match_first("""http://wiki.wolnepodreczniki.pl/Lektury:Anonim/Ala""", self.about_patterns)
        assert match_first("""http://wiki.wolnepodreczniki.pl/Lektury:Karpi%C5%84ski/Sielanki/Powr%C3%B3t_z_Warszawy_na_wie%C5%9B""", self.about_patterns)

    def read_file(self, path):
        return WLDocument.from_file(path)

    def run(self):
        for file in os.listdir(u"."):
            try:
                doc = self.read_file(file)
                about_link = unicode(doc.book_info.about)
                url = doc.book_info.url
                if not about_link:
                    if not url:
                        self.invalid.add(file)
                        continue
                    self.unrecognized[file] = url
                    continue

                m = match_first(about_link, self.about_patterns)
                if m:
                    if m in self.documents:
                        l = self.duplicates.get(m, [])
                        l.append(file)
                        self.duplicates[m] = l
                    else:
                        self.documents.add(m)
                else:
                    self.unrecognized[file] = about_link
            except Exception:
                self.invalid.add(file)



        print u"""\
{0} correct documents, 
{1} invalid,
{2} unrecognized,
\t{unrecognized}
{3} duplicate names
\t{duplicates}""".format(
            len(self.documents),
            len(self.invalid),
            len(self.unrecognized),
            len(self.duplicates),
            duplicates='\n\t'.join(repr(x) for x in self.duplicates.items()),
            unrecognized='\n\t'.join(repr(x) for x in self.unrecognized.items())
        )

        for doc in self.documents:
            print u"http://redakcja.wolnelektury.pl/documents/{0}".format('/'.join(doc).lower())


if __name__ == '__main__':

    task = Task()
    task.run()
