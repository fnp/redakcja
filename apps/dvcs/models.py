from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.base import ModelBase
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from mercurial import mdiff, simplemerge

from dvcs.fields import GzipFileSystemStorage
from dvcs.settings import REPO_PATH


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

    def next(self):
        """
            Returns the next tag - stage to work on.
            Returns None for the last stage.
        """
        try:
            return Tag.objects.filter(ordering__gt=self.ordering)[0]
        except IndexError:
            return None

models.signals.pre_save.connect(Tag.listener_changed, sender=Tag)


repo = GzipFileSystemStorage(location=REPO_PATH)

def data_upload_to(instance, filename):
    return "%d/%d" % (instance.tree.pk, instance.pk)

class Change(models.Model):
    """
        Single document change related to previous change. The "parent"
        argument points to the version against which this change has been 
        recorded. Initial text will have a null parent.
        
        Data file contains a gzipped text of the document.
    """
    author = models.ForeignKey(User, null=True, blank=True)
    author_name = models.CharField(max_length=128, null=True, blank=True)
    author_email = models.CharField(max_length=128, null=True, blank=True)
    data = models.FileField(upload_to=data_upload_to, storage=repo)
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
    publishable = models.BooleanField(default=False)

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
                self.revision = 0
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


def create_tag_model(model):
    name = model.__name__ + 'Tag'
    attrs = {
        '__module__': model.__module__,
    }
    return type(name, (Tag,), attrs)


def create_change_model(model):
    name = model.__name__ + 'Change'

    attrs = {
        '__module__': model.__module__,
        'tree': models.ForeignKey(model, related_name='change_set'),
        'tags': models.ManyToManyField(model.tag_model, related_name='change_set'),
    }
    return type(name, (Change,), attrs)



class DocumentMeta(ModelBase):
    "Metaclass for Document models."
    def __new__(cls, name, bases, attrs):
        model = super(DocumentMeta, cls).__new__(cls, name, bases, attrs)
        if not model._meta.abstract:
            # create a real Tag object and `stage' fk
            model.tag_model = create_tag_model(model)
            models.ForeignKey(model.tag_model, 
                null=True, blank=True).contribute_to_class(model, 'stage')

            # create real Change model and `head' fk
            model.change_model = create_change_model(model)
            models.ForeignKey(model.change_model,
                    null=True, blank=True, default=None,
                    help_text=_("This document's current head."),
                    editable=False).contribute_to_class(model, 'head')

        return model



class Document(models.Model):
    """
        File in repository.        
    """
    __metaclass__ = DocumentMeta

    creator = models.ForeignKey(User, null=True, blank=True, editable=False,
                related_name="created_documents")

    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        abstract = True

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

    def commit(self, text, **kwargs):
        if 'parent' not in kwargs:
            parent = self.head
        else:
            parent = kwargs['parent']
            if parent is not None and not isinstance(parent, Change):
                parent = self.change_set.objects.get(pk=kwargs['parent'])

        author = kwargs.get('author', None)
        author_name = kwargs.get('author_name', None)
        author_email = kwargs.get('author_email', None)
        tags = kwargs.get('tags', [])
        if tags:
            # set stage to next tag after the commited one
            self.stage = max(tags, key=lambda t: t.ordering).next()

        change = self.change_set.create(author=author,
                    author_name=author_name,
                    author_email=author_email,
                    description=kwargs.get('description', ''),
                    parent=parent)

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
        return self.head

    def history(self):
        return self.change_set.filter(revision__gt=-1)

    def revision(self):
        rev = self.change_set.aggregate(
                models.Max('revision'))['revision__max']
        return rev

    def at_revision(self, rev):
        """Returns a Change with given revision number."""
        return self.change_set.get(revision=rev)

    def publishable(self):
        changes = self.change_set.filter(publishable=True).order_by('-created_at')[:1]
        if changes.count():
            return changes[0]
        else:
            return None
