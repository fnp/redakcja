from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.contrib.comments.models import Comment
from django.template.defaultfilters import stringfilter
from django import template
from django.utils.translation import ugettext as _

from wiki.models import Book
from dvcs.models import Change

register = template.Library()


class Tab(object):
    slug = None
    caption = None
    url = None

    def __init__(self, slug, caption, url):
        self.slug = slug
        self.caption = caption
        self.url = url


@register.inclusion_tag("wiki/main_tabs.html", takes_context=True)
def main_tabs(context):
    active = getattr(context['request'], 'wiki_active_tab', None)

    tabs = []
    user = context['user']
    if user.is_authenticated():
        tabs.append(Tab('my', _('Assigned to me'), reverse("wiki_user")))

    tabs.append(Tab('unassigned', _('Unassigned'), reverse("wiki_unassigned")))
    tabs.append(Tab('users', _('Users'), reverse("wiki_users")))
    tabs.append(Tab('all', _('All'), reverse("wiki_document_list")))
    tabs.append(Tab('create', _('Add'), reverse("wiki_create_missing")))
    tabs.append(Tab('upload', _('Upload'), reverse("wiki_upload")))

    if user.is_staff:
        tabs.append(Tab('admin', _('Admin'), reverse("admin:index")))

    return {"tabs": tabs, "active_tab": active}


class WallItem(object):
    title = ''
    summary = ''
    url = ''
    timestamp = ''
    user = None
    email = ''

    def __init__(self, tag):
        self.tag = tag

    def get_email(self):
        if self.user:
            return self.user.email
        else:
            return self.email


def changes_wall(max_len):
    qs = Change.objects.filter(revision__gt=-1).order_by('-created_at').select_related()
    qs = qs[:max_len]
    for item in qs:
        tag = 'stage' if item.tags.count() else 'change'
        chunk = item.tree.chunk
        w  = WallItem(tag)
        w.title = chunk.pretty_name()
        w.summary = item.description
        w.url = reverse('wiki_editor', 
                args=[chunk.book.slug, chunk.slug]) + '?diff=%d' % item.revision
        w.timestamp = item.created_at
        w.user = item.author
        w.email = item.author_email
        yield w


def published_wall(max_len):
    qs = Book.objects.exclude(last_published=None).order_by('-last_published')
    qs = qs[:max_len]
    for item in qs:
        w  = WallItem('publish')
        w.title = item.title
        w.summary = item.title
        w.url = chunk.book.get_absolute_url()
        w.timestamp = item.last_published
        w.user = item.last_published_by
        yield w


def comments_wall(max_len):
    qs = Comment.objects.filter(is_public=True).select_related().order_by('-submit_date')
    qs = qs[:max_len]
    for item in qs:
        w  = WallItem('comment')
        w.title = item.content_object
        w.summary = item.comment
        w.url = item.content_object.get_absolute_url()
        w.timestamp = item.submit_date
        w.user = item.user
        w.email = item.user_email
        yield w


def big_wall(max_len, *args):
    """
        Takes some WallItem iterators and zips them into one big wall.
        Input iterators must already be sorted by timestamp.
    """
    subwalls = []
    for w in args:
        try:
            subwalls.append([next(w), w])
        except StopIteration:
            pass

    while max_len and subwalls:
        i, next_item = max(enumerate(subwalls), key=lambda x: x[1][0].timestamp)
        yield next_item[0]
        max_len -= 1
        try:
            next_item[0] = next(next_item[1])
        except StopIteration:
            del subwalls[i]


@register.inclusion_tag("wiki/wall.html", takes_context=True)
def wall(context, max_len=10):
    return {
        "request": context['request'],
        "STATIC_URL": context['STATIC_URL'],
        "wall": big_wall(max_len,
            changes_wall(max_len),
            published_wall(max_len),
            comments_wall(max_len),
        )}
