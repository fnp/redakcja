import sys
import docx
from lxml import etree


DEBUG = False

DC = "{http://purl.org/dc/elements/1.1/}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

ABOUT = "http://redakcja.wolnelektury.pl/documents/book/test-icm/"
WLURI = "http://wolnelektury.pl/katalog/lektura/test-icm/"



META_STYLES = { 
    "Author": DC + "creator",
    "Title": DC + "title",
    "Publisher": DC + "publisher",
    "Year": DC + "date",
    "Editor": DC + "contributor.editor",
    "Copyright holder": DC + "rights",
}


P_STYLES = {
    "Normal": "akap",
    "Autor": "autor_utworu",
    "Title": "nazwa_utworu",
    "Subtitle": "podtytul",
    "Heading 1": "naglowek_czesc",
    "Heading 2": "naglowek_rozdzial",
    "Heading 3": "naglowek_podrozdzial",
    "Heading 4": "srodtytul",
    "Heading 5": "srodtytul",

}


def wyroznienie(r):
    if r.font.italic is not None or r.font.bold is not None or r.font.underline is not None: return r.font.italic or r.font.bold or r.font.underline
    if r.style.font.italic is not None or r.style.font.bold is not None or r.style.font.underline is not None: return r.style.font.italic or r.style.font.bold or r.style.font.underline
    return False


def xml_from_docx(f):
    d = docx.Document(f)

    t = etree.Element("utwor")
    rdf = etree.SubElement(t, RDF + "RDF")
    meta = etree.SubElement(rdf, RDF + "Description")
    meta.attrib[RDF + "about"] = ABOUT

    etree.SubElement(meta, DC + "language").text = "pol"
    etree.SubElement(meta, DC + "identifier.url").text = WLURI

    m = etree.SubElement(t, "powiesc")
    md = {}

    for p in d.paragraphs:
        can_ignore = False
        if p.style.name == 'Title':
            md['title'] = p.text
        if p.style.name in META_STYLES:
            item = etree.SubElement(meta, META_STYLES[p.style.name])
            item.text = p.text
            can_ignore = True
        if p.style.name not in P_STYLES and not can_ignore:
            print(p.style.name, file=sys.stderr)
        if p.style.name in P_STYLES or not can_ignore:
            tag = P_STYLES.get(p.style.name, "akap")
            a = etree.SubElement(m, tag)

            for r in p.runs:
                if wyroznienie(r):
                    etree.SubElement(a, "wyroznienie").text = r.text
                else:
                    if len(a):
                        a[-1].tail = (a[-1].tail or '') + r.text
                    else:
                        a.text = (a.text or '') + r.text

            if DEBUG and p.style.name not in P_STYLES:
                a.text += f" [{p.style.name}]"

    return etree.tostring(t, pretty_print=True, encoding='unicode'), md
