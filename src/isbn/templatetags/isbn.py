from django.template import Library
from isbn.models import Isbn


register = Library()


@register.inclusion_tag('isbn/isbn_status.html', takes_context=True)
def isbn_status(context, book):
    user = context['request'].user
    formats = Isbn.formats_from_document(book)

    can_generate = False
    error = ''
    for f, v in formats:
        if not v:
            can_generate = True

    if can_generate:
        if not user.has_perm('isbn.add_isbn'):
            can_generate = False

    if can_generate:
        try:
            book.catalogue_book
        except:
            can_generate = False
            error = 'Brak książki w katalogu.'

    return {
        'book': book,
        'formats': formats,
        'can_generate': can_generate,
        'error': error,
    }

