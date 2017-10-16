# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
import os.path

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models.base import ModelBase
from django.utils.translation import string_concat, ugettext_lazy as _
from mercurial import simplemerge

from django.conf import settings
from dvcs.signals import post_commit, post_publishable
from dvcs.storage import GzipFileSystemStorage


class Tag(models.Model):
    """A tag (e.g. document stage) which can be applied to a Change."""
    name = models.CharField(_('name'), max_length=64)
    slug = models.SlugField(_('slug'), unique=True, max_length=64, null=True, blank=True)
    ordering = models.IntegerField(_('ordering'))

    _object_cache = {}

    class Meta:
        abstract = True
        ordering = ['ordering']

    def __unicode__(self):
        return self.name

    @classmethod
    def get(cls, slug):
        if slug in cls._object_cache:
            return cls._object_cache[slug]
        else:
            obj = cls.objects.get(slug=slug)
            cls._object_cache[slug] = obj
            return obj

    @staticmethod
    def listener_changed(sender, instance, **kwargs):
        sender._object_cache = {}

    def get_next(self):
        """
            Returns the next tag - stage to work on.
            Returns None for the last stage.
        """
        try:
            return type(self).objects.filter(ordering__gt=self.ordering)[0]
        except IndexError:
            return None

models.signals.pre_save.connect(Tag.listener_changed, sender=Tag)


def data_upload_to(instance, filename):
    return "%d/%d" % (instance.tree.pk, instance.pk)


class Change(models.Model):
    """
        Single document change related to previous change. The "parent"
        argument points to the version against which this change has been 
        recorded. Initial text will have a null parent.
        
        Data file contains a gzipped text of the document.
    """
    author = models.ForeignKey(User, null=True, blank=True, verbose_name=_('author'))
    author_name = models.CharField(
        _('author name'), max_length=128, null=True, blank=True, help_text=_("Used if author is not set."))
    author_email = models.CharField(
        _('author email'), max_length=128, null=True, blank=True, help_text=_("Used if author is not set."))
    revision = models.IntegerField(_('revision'), db_index=True)

    parent = models.ForeignKey(
        'self', null=True, blank=True, default=None, verbose_name=_('parent'), related_name="children")

    merge_parent = models.ForeignKey(
        'self', null=True, blank=True, default=None, verbose_name=_('merge parent'), related_name="merge_children")

    description = models.TextField(_('description'), blank=True, default='')
    created_at = models.DateTimeField(editable=False, db_index=True, default=datetime.now)
    publishable = models.BooleanField(_('publishable'), default=False)

    class Meta:
        abstract = True
        ordering = ('created_at',)
        unique_together = ['tree', 'revision']

    def __unicode__(self):
        return u"Id: %r, Tree %r, Parent %r, Data: %s" % (self.id, self.tree_id, self.parent_id, self.data)

    def author_str(self):
        if self.author:
            return "%s %s <%s>" % (
                self.author.first_name,
                self.author.last_name, 
                self.author.email)
        else:
            return "%s <%s>" % (
                self.author_name,
                self.author_email
                )

    def save(self, *args, **kwargs):
        """
            take the next available revision number if none yet
        """
        if self.revision is None:
            tree_rev = self.tree.revision()
            if tree_rev is None:
                self.revision = 1
            else:
                self.revision = tree_rev + 1
        return super(Change, self).save(*args, **kwargs)

    def materialize(self):
        f = self.data.storage.open(self.data)
        text = f.read()
        f.close()
        return unicode(text, 'utf-8')

    def merge_with(self, other, author=None, 
            author_name=None, author_email=None, 
            description=u"Automatic merge."):
        """Performs an automatic merge after straying commits."""
        assert self.tree_id == other.tree_id  # same tree
        if other.parent_id == self.pk:
            # immediate child - fast forward
            return other

        local = self.materialize().encode('utf-8')
        base = other.parent.materialize().encode('utf-8')
        remote = other.materialize().encode('utf-8')

        merge = simplemerge.Merge3Text(base, local, remote)
        result = ''.join(merge.merge_lines())
        merge_node = self.children.create(
                    merge_parent=other, tree=self.tree,
                    author=author,
                    author_name=author_name,
                    author_email=author_email,
                    description=description)
        merge_node.data.save('', ContentFile(result))
        return merge_node

    def revert(self, **kwargs):
        """ commit this version of a doc as new head """
        self.tree.commit(text=self.materialize(), **kwargs)

    def set_publishable(self, publishable):
        self.publishable = publishable
        self.save()
        post_publishable.send(sender=self, publishable=publishable)


def create_tag_model(model):
    name = model.__name__ + 'Tag'

    class Meta(Tag.Meta):
        app_label = model._meta.app_label
        verbose_name = string_concat(
            _("tag"), " ", _("for:"), " ", model._meta.verbose_name)
        verbose_name_plural = string_concat(
            _("tags"), " ", _("for:"), " ", model._meta.verbose_name)

    attrs = {
        '__module__': model.__module__,
        'Meta': Meta,
    }
    return type(name, (Tag,), attrs)


def create_change_model(model):
    name = model.__name__ + 'Change'
    repo = GzipFileSystemStorage(location=model.REPO_PATH)

    class Meta(Change.Meta):
        app_label = model._meta.app_label
        verbose_name = string_concat(
            _("change"), " ", _("for:"), " ", model._meta.verbose_name)
        verbose_name_plural = string_concat(
            _("changes"), " ", _("for:"), " ", model._meta.verbose_name)

    attrs = {
        '__module__': model.__module__,
        'tree': models.ForeignKey(model, related_name='change_set', verbose_name=_('document')),
        'tags': models.ManyToManyField(model.tag_model, verbose_name=_('tags'), related_name='change_set'),
        'data': models.FileField(_('data'), upload_to=data_upload_to, storage=repo),
        'Meta': Meta,
    }
    return type(name, (Change,), attrs)


class DocumentMeta(ModelBase):
    """Metaclass for Document models."""
    def __new__(cls, name, bases, attrs):

        model = super(DocumentMeta, cls).__new__(cls, name, bases, attrs)
        if not model._meta.abstract:
            # create a real Tag object and `stage' fk
            model.tag_model = create_tag_model(model)
            models.ForeignKey(model.tag_model, verbose_name=_('stage'),
                null=True, blank=True).contribute_to_class(model, 'stage')

            # create real Change model and `head' fk
            model.change_model = create_change_model(model)

            models.ForeignKey(
                model.change_model, null=True, blank=True, default=None,
                verbose_name=_('head'), help_text=_("This document's current head."),
                editable=False).contribute_to_class(model, 'head')

            models.ForeignKey(
                User, null=True, blank=True, editable=False,
                verbose_name=_('creator'), related_name="created_%s" % name.lower()
                ).contribute_to_class(model, 'creator')

        return model


class Document(models.Model):
    """File in repository. Subclass it to use version control in your app."""

    __metaclass__ = DocumentMeta

    # default repository path
    REPO_PATH = os.path.join(settings.MEDIA_ROOT, 'dvcs')

    user = models.ForeignKey(User, null=True, blank=True, verbose_name=_('user'), help_text=_('Work assignment.'))

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"{0}, HEAD: {1}".format(self.id, self.head_id)

    def materialize(self, change=None):
        if self.head is None:
            return u''
        if change is None:
            change = self.head
        elif not isinstance(change, Change):
            change = self.change_set.get(pk=change)
        return change.materialize()

    def commit(self, text, author=None, author_name=None, author_email=None, publishable=False, **kwargs):
        """Commits a new revision.

        This will automatically merge the commit into the main branch,
        if parent is not document's head.

        :param unicode text: new version of the document
        :param parent: parent revision (head, if not specified)
        :type parent: Change or None
        :param User author: the commiter
        :param unicode author_name: commiter name (if ``author`` not specified)
        :param unicode author_email: commiter e-mail (if ``author`` not specified)
        :param Tag[] tags: list of tags to apply to the new commit
        :param bool publishable: set new commit as ready to publish
        :returns: new head
        """
        if 'parent' not in kwargs:
            parent = self.head
        else:
            parent = kwargs['parent']
            if parent is not None and not isinstance(parent, Change):
                parent = self.change_set.objects.get(pk=kwargs['parent'])

        tags = kwargs.get('tags', [])
        if tags:
            # set stage to next tag after the commited one
            self.stage = max(tags, key=lambda t: t.ordering).get_next()

        change = self.change_set.create(
            author=author, author_name=author_name, author_email=author_email,
            description=kwargs.get('description', ''), publishable=publishable, parent=parent)

        change.tags = tags
        change.data.save('', ContentFile(text.encode('utf-8')))
        change.save()

        if self.head:
            # merge new change as new head
            self.head = self.head.merge_with(change, author=author,
                    author_name=author_name,
                    author_email=author_email)
        else:
            self.head = change
        self.save()

        post_commit.send(sender=self.head)

        return self.head

    def history(self):
        return self.change_set.all().order_by('revision')

    def revision(self):
        rev = self.change_set.aggregate(
                models.Max('revision'))['revision__max']
        return rev

    def at_revision(self, rev):
        """Returns a Change with given revision number."""
        return self.change_set.get(revision=rev)

    def publishable(self):
        changes = self.history().filter(publishable=True)
        if changes.exists():
            return changes.order_by('-revision')[0]
        else:
            return None

    @transaction.atomic
    def prepend_history(self, other):
        """Takes over the the other document's history and prepends to own."""

        assert self != other
        other_revs = other.change_set.all().count()
        # workaround for a non-atomic UPDATE in SQLITE
        self.change_set.all().update(revision=0-models.F('revision'))
        self.change_set.all().update(revision=other_revs - models.F('revision'))
        other.change_set.all().update(tree=self)
        assert not other.change_set.exists()
        other.delete()
