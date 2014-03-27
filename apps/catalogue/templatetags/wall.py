from __future__ import absolute_import

from datetime import timedelta
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.comments.models import Comment
from django import template
from django.utils.translation import ugettext as _

from catalogue.models import Chunk, BookPublishRecord, Image, ImagePublishRecord

register = template.Library()


class WallItem(object):
    title = ''
    summary = ''
    url = ''
    timestamp = ''
    user = None
    user_name = ''
    email = ''

    def __init__(self, tag):
        self.tag = tag

    def get_email(self):
        if self.user:
            return self.user.email
        else:
            return self.email


def changes_wall(user=None, max_len=None, day=None):
    qs = Chunk.change_model.objects.order_by('-created_at')
    qs = qs.select_related('author', 'tree', 'tree__book__title')
    if user is not None:
        qs = qs.filter(Q(author=user) | Q(tree__user=user))
    if max_len is not None:
        qs = qs[:max_len]
    if day is not None:
        next_day = day + timedelta(1)
        qs = qs.filter(created_at__gte=day, created_at__lt=next_day)
    for item in qs:
        tag = 'stage' if item.tags.count() else 'change'
        chunk = item.tree
        w  = WallItem(tag)
        if user and item.author != user:
            w.header = _('Related edit')
        else:
            w.header = _('Edit')
        w.title = chunk.pretty_name()
        w.summary = item.description
        w.url = reverse('wiki_editor', 
                args=[chunk.book.slug, chunk.slug]) + '?diff=%d' % item.revision
        w.timestamp = item.created_at
        w.user = item.author
        w.user_name = item.author_name
        w.email = item.author_email
        yield w


def image_changes_wall(user=None, max_len=None, day=None):
    qs = Image.change_model.objects.order_by('-created_at')
    qs = qs.select_related('author', 'tree', 'tree__title')
    if user is not None:
        qs = qs.filter(Q(author=user) | Q(tree__user=user))
    if max_len is not None:
        qs = qs[:max_len]
    if day is not None:
        next_day = day + timedelta(1)
        qs = qs.filter(created_at__gte=day, created_at__lt=next_day)
    for item in qs:
        tag = 'stage' if item.tags.count() else 'change'
        image = item.tree
        w  = WallItem(tag)
        if user and item.author != user:
            w.header = _('Related edit')
        else:
            w.header = _('Edit')
        w.title = image.title
        w.summary = item.description
        w.url = reverse('wiki_img_editor', 
                args=[image.slug]) + '?diff=%d' % item.revision
        w.timestamp = item.created_at
        w.user = item.author
        w.user_name = item.author_name
        w.email = item.author_email
        yield w



# TODO: marked for publishing


def published_wall(user=None, max_len=None, day=None):
    qs = BookPublishRecord.objects.select_related('book__title')
    if user:
        # TODO: published my book
        qs = qs.filter(Q(user=user))
    if max_len is not None:
        qs = qs[:max_len]
    if day is not None:
        next_day = day + timedelta(1)
        qs = qs.filter(timestamp__gte=day, timestamp__lt=next_day)
    for item in qs:
        w = WallItem('publish')
        w.header = _('Publication')
        w.title = item.book.title
        w.timestamp = item.timestamp
        w.url = item.book.get_absolute_url()
        w.user = item.user
        w.email = item.user.email
        yield w


def image_published_wall(user=None, max_len=None, day=None):
    qs = ImagePublishRecord.objects.select_related('image__title')
    if user:
        # TODO: published my book
        qs = qs.filter(Q(user=user))
    if max_len is not None:
        qs = qs[:max_len]
    if day is not None:
        next_day = day + timedelta(1)
        qs = qs.filter(timestamp__gte=day, timestamp__lt=next_day)
    for item in qs:
        w = WallItem('publish')
        w.header = _('Publication')
        w.title = item.image.title
        w.timestamp = item.timestamp
        w.url = item.image.get_absolute_url()
        w.user = item.user
        w.email = item.user.email
        yield w


def comments_wall(user=None, max_len=None, day=None):
    qs = Comment.objects.filter(is_public=True).select_related().order_by('-submit_date')
    if user:
        # TODO: comments concerning my books
        qs = qs.filter(Q(user=user))
    if max_len is not None:
        qs = qs[:max_len]
    if day is not None:
        next_day = day + timedelta(1)
        qs = qs.filter(submit_date__gte=day, submit_date__lt=next_day)
    for item in qs:
        w  = WallItem('comment')
        w.header = _('Comment')
        w.title = item.content_object
        w.summary = item.comment
        w.url = item.content_object.get_absolute_url()
        w.timestamp = item.submit_date
        w.user = item.user
        ui = item.userinfo
        w.email = item.email
        w.user_name = item.name
        yield w


def big_wall(walls, max_len=None):
    """
        Takes some WallItem iterators and zips them into one big wall.
        Input iterators must already be sorted by timestamp.
    """
    subwalls = []
    for w in walls:
        try:
            subwalls.append([next(w), w])
        except StopIteration:
            pass

    if max_len is None:
        max_len = -1
    while max_len and subwalls:
        i, next_item = max(enumerate(subwalls), key=lambda x: x[1][0].timestamp)
        yield next_item[0]
        max_len -= 1
        try:
            next_item[0] = next(next_item[1])
        except StopIteration:
            del subwalls[i]


@register.inclusion_tag("catalogue/wall.html", takes_context=True)
def wall(context, user=None, max_len=100):
    return {
        "request": context['request'],
        "STATIC_URL": context['STATIC_URL'],
        "wall": big_wall([
            changes_wall(user, max_len),
            published_wall(user, max_len),
            image_changes_wall(user, max_len),
            image_published_wall(user, max_len),
            comments_wall(user, max_len),
        ], max_len)}

@register.inclusion_tag("catalogue/wall.html", takes_context=True)
def day_wall(context, day):
    return {
        "request": context['request'],
        "STATIC_URL": context['STATIC_URL'],
        "wall": big_wall([
            changes_wall(day=day),
            published_wall(day=day),
            image_changes_wall(day=day),
            image_published_wall(day=day),
            comments_wall(day=day),
        ])}
