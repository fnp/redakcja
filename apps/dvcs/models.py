from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from mercurial import mdiff, simplemerge
import pickle


class Tag(models.Model):
    """
        a tag (e.g. document stage) which can be applied to a change
    """

    name = models.CharField(_('name'), max_length=64)
    slug = models.SlugField(_('slug'), unique=True, max_length=64, 
            null=True, blank=True)
    ordering = models.IntegerField(_('ordering'))

    _object_cache = {}

    class Meta:
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

models.signals.pre_save.connect(Tag.listener_changed, sender=Tag)


class Change(models.Model):
    """
        Single document change related to previous change. The "parent"
        argument points to the version against which this change has been 
        recorded. Initial text will have a null parent.
        
        Data contains a pickled diff needed to reproduce the initial document.
    """
    author = models.ForeignKey(User, null=True, blank=True)
    author_desc = models.CharField(max_length=128, null=True, blank=True)
    patch = models.TextField(blank=True)
    tree = models.ForeignKey('Document')
    revision = models.IntegerField(db_index=True)

    parent = models.ForeignKey('self',
                        null=True, blank=True, default=None,
                        related_name="children")

    merge_parent = models.ForeignKey('self',
                        null=True, blank=True, default=None,
                        related_name="merge_children")

    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(editable=False, db_index=True, 
                        default=datetime.now)

    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ('created_at',)
        unique_together = ['tree', 'revision']

    def __unicode__(self):
        return u"Id: %r, Tree %r, Parent %r, Patch '''\n%s'''" % (self.id, self.tree_id, self.parent_id, self.patch)

    def author_str(self):
        if self.author:
            return "%s %s <%s>" % (
                self.author.first_name,
                self.author.last_name, 
                self.author.email)
        else:
            return self.author_desc


    def save(self, *args, **kwargs):
        """
            take the next available revision number if none yet
        """
        if self.revision is None:
            self.revision = self.tree.revision() + 1
        return super(Change, self).save(*args, **kwargs)

    @staticmethod
    def make_patch(src, dst):
        if isinstance(src, unicode):
            src = src.encode('utf-8')
        if isinstance(dst, unicode):
            dst = dst.encode('utf-8')
        return pickle.dumps(mdiff.textdiff(src, dst))

    def materialize(self):
        # special care for merged nodes
        if self.parent is None and self.merge_parent is not None:
            return self.apply_to(self.merge_parent.materialize())

        changes = Change.objects.exclude(parent=None).filter(
                        tree=self.tree,
                        revision__lte=self.revision).order_by('revision')
        text = u''
        for change in changes:
            text = change.apply_to(text)
        return text

    def make_child(self, patch, description, author=None,
            author_desc=None, tags=None):
        ch = self.children.create(patch=patch,
                        tree=self.tree, author=author,
                        author_desc=author_desc,
                        description=description)
        if tags is not None:
            ch.tags = tags
        return ch

    def make_merge_child(self, patch, description, author=None, 
            author_desc=None, tags=None):
        ch = self.merge_children.create(patch=patch,
                        tree=self.tree, author=author,
                        author_desc=author_desc,
                        description=description,
                        tags=tags)
        if tags is not None:
            ch.tags = tags
        return ch

    def apply_to(self, text):
        return mdiff.patch(text, pickle.loads(self.patch.encode('ascii')))

    def merge_with(self, other, author=None, author_desc=None,
            description=u"Automatic merge."):
        assert self.tree_id == other.tree_id  # same tree
        if other.parent_id == self.pk:
            # immediate child 
            return other

        local = self.materialize()
        base = other.merge_parent.materialize()
        remote = other.apply_to(base)

        merge = simplemerge.Merge3Text(base, local, remote)
        result = ''.join(merge.merge_lines())
        patch = self.make_patch(local, result)
        return self.children.create(
                    patch=patch, merge_parent=other, tree=self.tree,
                    author=author, author_desc=author_desc,
                    description=description)

    def revert(self, **kwargs):
        """ commit this version of a doc as new head """
        self.tree.commit(text=self.materialize(), **kwargs)


class Document(models.Model):
    """
        File in repository.        
    """
    creator = models.ForeignKey(User, null=True, blank=True, editable=False)
    head = models.ForeignKey(Change,
                    null=True, blank=True, default=None,
                    help_text=_("This document's current head."),
                    editable=False)

    def __unicode__(self):
        return u"{0}, HEAD: {1}".format(self.id, self.head_id)

    @models.permalink
    def get_absolute_url(self):
        return ('dvcs.views.document_data', (), {
                        'document_id': self.id,
                        'version': self.head_id,
        })

    def materialize(self, change=None):
        if self.head is None:
            return u''
        if change is None:
            change = self.head
        elif not isinstance(change, Change):
            change = self.change_set.get(pk=change)
        return change.materialize()

    def commit(self, **kwargs):
        if 'parent' not in kwargs:
            parent = self.head
        else:
            parent = kwargs['parent']
            if not isinstance(parent, Change):
                parent = Change.objects.get(pk=kwargs['parent'])

        if 'patch' not in kwargs:
            if 'text' not in kwargs:
                raise ValueError("You must provide either patch or target document.")
            patch = Change.make_patch(self.materialize(change=parent), kwargs['text'])
        else:
            if 'text' in kwargs:
                raise ValueError("You can provide only text or patch - not both")
            patch = kwargs['patch']

        author = kwargs.get('author', None)
        author_desc = kwargs.get('author_desc', None)
        tags = kwargs.get('tags', [])

        old_head = self.head
        if parent != old_head:
            change = parent.make_merge_child(patch, author=author, 
                    author_desc=author_desc,
                    description=kwargs.get('description', ''),
                    tags=tags)
            # not Fast-Forward - perform a merge
            self.head = old_head.merge_with(change, author=author,
                    author_desc=author_desc)
        else:
            self.head = parent.make_child(patch, author=author, 
                    author_desc=author_desc, 
                    description=kwargs.get('description', ''),
                    tags=tags)

        self.save()
        return self.head

    def history(self):
        return self.change_set.filter(revision__gt=-1)

    def revision(self):
        rev = self.change_set.aggregate(
                models.Max('revision'))['revision__max']
        return rev if rev is not None else -1

    def at_revision(self, rev):
        if rev:
            return self.change_set.get(revision=rev)
        else:
            return self.head

    def last_tagged(self, tag):
        changes = tag.change_set.filter(tree=self).order_by('-created_at')[:1]
        if changes.count():
            return changes[0]
        else:
            return None

    @staticmethod
    def listener_initial_commit(sender, instance, created, **kwargs):
        # run for Document and its subclasses
        if not isinstance(instance, Document):
            return
        if created:
            instance.head = Change.objects.create(
                    revision=-1,
                    author=instance.creator,
                    patch=Change.make_patch('', ''),
                    tree=instance)
            instance.save()

models.signals.post_save.connect(Document.listener_initial_commit)
