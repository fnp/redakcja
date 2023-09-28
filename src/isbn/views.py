from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404, redirect
from librarian import DCNS, RDFNS
from lxml import etree
from documents.models import Book
from .models import Isbn, IsbnPool


def isbn_list(request):
    return render(request, 'isbn/list.html', {
        'pools': IsbnPool.objects.all(),
        'list': Isbn.objects.all(),
    })


MIME = {
    'html': 'text/html',
    'pdf': 'application/pdf',
    'txt': 'text/plain',
    'epub': 'application/epub+zip',
    'mobi': 'application/x-mobipocket-ebook',
}


@permission_required('isbn.add_isbn')
def generate(request, document_id):
    document = get_object_or_404(Book, id=document_id)
    book = document.catalogue_book
    chunk = document[0]
    head = chunk.head
    orig_xml = head.materialize()
    tree = etree.fromstring(orig_xml)
    rdfdesc = tree.find('.//' + RDFNS('Description'))

    for form, value in Isbn.formats_from_document(document):
        if value: continue
        isbn = Isbn.get_for_book(book, form)

        etree.SubElement(rdfdesc, DCNS('relation.hasFormat'), id="mobi").text = f"https://wolnelektury.pl/media/book/{form}mobi/{book.slug}.{form}"
        etree.SubElement(
            rdfdesc, 'meta', refines=f'#{form}', id=f'{form}-id', property='dcterms:identifier'
        ).text = 'ISBN-' + isbn.get_code(True)
        etree.SubElement(rdfdesc, 'meta', refines=f'#{form}-id', property='identifier-type').text = 'ISBN'
        etree.SubElement(rdfdesc, 'meta', refines=f'#{form}', property='dcterms:format').text = MIME[form]

    xml = etree.tostring(tree, encoding='unicode')
    chunk.commit(
        text=xml,
        author=request.user,
        parent=head,
        description='Auto ISBN',
        publishable=head.publishable
    )

    return redirect(document.get_absolute_url())
