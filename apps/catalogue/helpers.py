from functools import wraps

from django.db.models import Count


def active_tab(tab):
    """
        View decorator, which puts tab info on a request.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(request, *args, **kwargs):
            request.catalogue_active_tab = tab
            return f(request, *args, **kwargs)
        return wrapped
    return wrapper


class ChunksList(object):
    def __init__(self, chunk_qs):
        self.chunk_qs = chunk_qs.annotate(
            book_length=Count('book__chunk')).select_related(
            'book', 'stage__name',
            'user')

        self.book_qs = chunk_qs.values('book_id')

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.get_slice(key)
        elif isinstance(key, int):
            return self.get_slice(slice(key, key+1))[0]
        else:
            raise TypeError('Unsupported list index. Must be a slice or an int.')

    def __len__(self):
        return self.book_qs.count()

    def get_slice(self, slice_):
        book_ids = [x['book_id'] for x in self.book_qs[slice_]]
        chunk_qs = self.chunk_qs.filter(book__in=book_ids)

        chunks_list = []
        book = None
        for chunk in chunk_qs:
            if chunk.book != book:
                book = chunk.book
                chunks_list.append(ChoiceChunks(book, [chunk], chunk.book_length))
            else:
                chunks_list[-1].chunks.append(chunk)
        return chunks_list


class ChoiceChunks(object):
    """
        Associates the given chunks iterable for a book.
    """

    chunks = None

    def __init__(self, book, chunks, book_length):
        self.book = book
        self.chunks = chunks
        self.book_length = book_length

