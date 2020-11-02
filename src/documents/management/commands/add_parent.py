# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys

from datetime import date
from lxml import etree

from django.core.management import BaseCommand

from documents.models import Book
from librarian import RDFNS, DCNS

TEMPLATE = '''<utwor>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="http://redakcja.wolnelektury.pl/documents/book/%(slug)s/">
%(dc)s
</rdf:Description>
</rdf:RDF>

</utwor>
'''

DC_TEMPLATE = '<dc:%(tag)s xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">%(value)s</dc:%(tag)s>'

DC_TAGS = (
    'creator',
    'title',
    'relation.hasPart',
    'contributor.translator',
    'contributor.editor',
    'contributor.technical_editor',
    'contributor.funding',
    'contributor.thanks',
    'publisher',
    'subject.period',
    'subject.type',
    'subject.genre',
    'description',
    'identifier.url',
    'source',
    'source.URL',
    'rights.license',
    'rights',
    'date.pd',
    'format',
    'type',
    'date',
    'audience',
    'language',
)

IDENTIFIER_PREFIX = 'http://wolnelektury.pl/katalog/lektura/'


def dc_desc_element(book):
    xml = book.materialize()
    tree = etree.fromstring(xml)
    return tree.find(".//" + RDFNS("Description"))


def distinct_dc_values(tag, desc_elements):
    values = set()
    for desc in desc_elements:
        values.update(elem.text for elem in desc.findall(DCNS(tag)))
    return values


class Command(BaseCommand):
    args = 'slug'

    def handle(self, slug, **options):
        children_slugs = [line.strip() for line in sys.stdin]
        children = Book.objects.filter(catalogue_book_id__in=children_slugs)
        desc_elements = [dc_desc_element(child) for child in children]
        title = u'Utwory wybrane'
        own_attributes = {
            'title': title,
            'relation.hasPart': [IDENTIFIER_PREFIX + child_slug for child_slug in children_slugs],
            'identifier.url': IDENTIFIER_PREFIX + slug,
            'date': date.today().isoformat(),
        }
        dc_tags = []
        for tag in DC_TAGS:
            if tag in own_attributes:
                values = own_attributes[tag]
                if not isinstance(values, list):
                    values = [values]
            else:
                values = distinct_dc_values(tag, desc_elements)
            for value in values:
                dc_tags.append(DC_TEMPLATE % {'tag': tag, 'value': value})
        xml = TEMPLATE % {'slug': slug, 'dc': '\n'.join(dc_tags)}
        Book.create(
            text=xml,
            creator=None,
            slug=slug,
            title=title,
            gallery=slug)
