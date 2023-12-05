import os
from librarian import RDFNS, DCNS
from lxml import etree
from datetime import date
from . import ocr
from django.conf import settings


def build_document_texts(book_source):
    texts = []
    for builder in text_builders:
        root = etree.Element('utwor')
        # add meta
        add_rdf(root, book_source)

        # add master
        master = etree.SubElement(root, 'powiesc')

        for page in book_source.get_ocr_files():
            builder(master, page)
    
        texts.append(etree.tostring(root, encoding='unicode', pretty_print=True))
    return texts


text_builders = [
    ocr.add_page_to_master,
    ocr.add_page_to_master_as_stanzas,
    ocr.add_page_to_master_as_p,
]


def add_rdf(root, book_source):
    book = book_source.book
    
    # TODO: to librarian
    rdf = etree.SubElement(root, RDFNS('RDF'))
    desc = etree.SubElement(rdf, RDFNS('Description'), **{})

    # author
    for author in book.authors.all():
        etree.SubElement(desc, DCNS('creator')).text = f'{author.last_name_pl}, {author.first_name_pl}'
    # translator
    for tr in book.translators.all():
        etree.SubElement(desc, DCNS('contributor.translator')).text = f'{tr.last_name_pl}, {tr.first_name_pl}'
    # title
    etree.SubElement(desc, DCNS('title')).text = book.title
    # created_at
    etree.SubElement(desc, DCNS('date')).text = date.today().isoformat()
    # date.pd
    etree.SubElement(desc, DCNS('date.pd')).text = str(book.pd_year)
    #publisher
    etree.SubElement(desc, DCNS('publisher')). text = 'Fundacja Wolne Lektury'
    #language
    etree.SubElement(desc, DCNS('language')).text = book.language # 3to2?
    #description
    #source_name
    etree.SubElement(desc, DCNS('source')).text = book_source.source.name
    #url
    etree.SubElement(desc, DCNS('identifier.url')).text = f'https://wolnelektury.pl/katalog/lektura/{book.slug}/'
    #license?
    #license_description?
    etree.SubElement(desc, DCNS('rights')).text = ''
    #epochs
    for tag in book.epochs.all():
        etree.SubElement(desc, DCNS('subject.period')).text = tag.name
    #kinds
    for tag in book.kinds.all():
        etree.SubElement(desc, DCNS('subject.type')).text = tag.name
    #genres
    for tag in book.genres.all():
        etree.SubElement(desc, DCNS('subject.genre')).text = tag.name

    
