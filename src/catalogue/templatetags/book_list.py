from __future__ import absolute_import

from re import split
from django.db.models import Q, Count
from django import template
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from catalogue.models import Chunk, Image, Project

register = template.Library()


class ChunksList(object):
    def __init__(self, chunk_qs):
        self.chunk_qs = chunk_qs.select_related('book', 'book__project', 'stage', 'user')
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
                chunks_list.append(ChoiceChunks(book, [chunk]))
            else:
                chunks_list[-1].chunks.append(chunk)
        return chunks_list


class ChoiceChunks(object):
    """
        Associates the given chunks iterable for a book.
    """

    chunks = None

    def __init__(self, book, chunks):
        self.book = book
        self.chunks = chunks


def foreign_filter(qs, value, filter_field, model, model_field='slug', unset='-'):
    if value == unset:
        return qs.filter(**{filter_field: None})
    if not value:
        return qs
    try:
        obj = model._default_manager.get(**{model_field: value})
    except model.DoesNotExist:
        return qs.none()
    else:
        return qs.filter(**{filter_field: obj})


def search_filter(qs, value, filter_fields):
    if not value:
        return qs
    q = Q(**{"%s__icontains" % filter_fields[0]: value})
    for field in filter_fields[1:]:
        q |= Q(**{"%s__icontains" % field: value})
    return qs.filter(q)


_states = [
        ('publishable', _('publishable'), Q(book___new_publishable=True)),
        ('changed', _('changed'), Q(_changed=True)),
        ('published', _('published'), Q(book___published=True)),
        ('unpublished', _('unpublished'), Q(book___published=False)),
        ('empty', _('empty'), Q(head=None)),
    ]
_states_options = [s[:2] for s in _states]
_states_dict = dict([(s[0], s[2]) for s in _states])


def document_list_filter(request, **kwargs):

    def arg_or_GET(field):
        return kwargs.get(field, request.GET.get(field))

    if arg_or_GET('all'):
        chunks = Chunk.objects.all()
    else:
        chunks = Chunk.visible_objects.all()

    chunks = chunks.order_by('book__title', 'book', 'number')

    if not request.user.is_authenticated():
        chunks = chunks.filter(book__public=True)

    state = arg_or_GET('status')
    if state in _states_dict:
        chunks = chunks.filter(_states_dict[state])

    chunks = foreign_filter(chunks, arg_or_GET('user'), 'user', User, 'username')
    chunks = foreign_filter(chunks, arg_or_GET('stage'), 'stage', Chunk.tag_model, 'slug')
    chunks = search_filter(chunks, arg_or_GET('title'), ['book__title', 'title'])
    chunks = foreign_filter(chunks, arg_or_GET('project'), 'book__project', Project, 'pk')
    return chunks


@register.inclusion_tag('catalogue/book_list/book_list.html', takes_context=True)
def book_list(context, user=None):
    request = context['request']

    if user:
        filters = {"user": user}
        new_context = {"viewed_user": user}
    else:
        filters = {}
        new_context = {
            "users": User.objects.annotate(
                count=Count('chunk')).filter(count__gt=0).order_by(
                '-count', 'last_name', 'first_name'),
            "other_users": User.objects.annotate(
                count=Count('chunk')).filter(count=0).order_by(
                'last_name', 'first_name'),
                }

    new_context.update({
        "filters": True,
        "request": request,
        "books": ChunksList(document_list_filter(request, **filters)),
        "stages": Chunk.tag_model.objects.all(),
        "states": _states_options,
        "projects": Project.objects.all(),
    })

    return new_context



_image_states = [
        ('publishable', _('publishable'), Q(_new_publishable=True)),
        ('changed', _('changed'), Q(_changed=True)),
        ('published', _('published'), Q(_published=True)),
        ('unpublished', _('unpublished'), Q(_published=False)),
        ('empty', _('empty'), Q(head=None)),
    ]
_image_states_options = [s[:2] for s in _image_states]
_image_states_dict = dict([(s[0], s[2]) for s in _image_states])

def image_list_filter(request, **kwargs):

    def arg_or_GET(field):
        return kwargs.get(field, request.GET.get(field))

    images = Image.objects.all().select_related('user', 'stage', 'project')

    if not request.user.is_authenticated():
        images = images.filter(public=True)

    state = arg_or_GET('status')
    if state in _image_states_dict:
        images = images.filter(_image_states_dict[state])

    images = foreign_filter(images, arg_or_GET('user'), 'user', User, 'username')
    images = foreign_filter(images, arg_or_GET('stage'), 'stage', Image.tag_model, 'slug')
    images = search_filter(images, arg_or_GET('title'), ['title', 'title'])
    images = foreign_filter(images, arg_or_GET('project'), 'project', Project, 'pk')
    return images


@register.inclusion_tag('catalogue/image_table.html', takes_context=True)
def image_list(context, user=None):
    request = context['request']

    if user:
        filters = {"user": user}
        new_context = {"viewed_user": user}
    else:
        filters = {}
        new_context = {
            "users": User.objects.annotate(
                count=Count('image')).filter(count__gt=0).order_by(
                '-count', 'last_name', 'first_name'),
            "other_users": User.objects.annotate(
                count=Count('image')).filter(count=0).order_by(
                'last_name', 'first_name'),
                }

    new_context.update({
        "filters": True,
        "request": request,
        "objects": image_list_filter(request, **filters),
        "stages": Image.tag_model.objects.all(),
        "states": _image_states_options,
        "projects": Project.objects.all(),
    })

    return new_context
