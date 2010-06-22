from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from mercurial import mdiff, simplemerge
import pickle

class Change(models.Model):
    """
        Single document change related to previous change. The "parent"
        argument points to the version against which this change has been 
        recorded. Initial text will have a null parent.
        
        Data contains a pickled diff needed to reproduce the initial document.
    """
    author = models.ForeignKey(User)
    patch = models.TextField(blank=True)
    tree = models.ForeignKey('Document')

    parent = models.ForeignKey('self',
                        null=True, blank=True, default=None,
                        related_name="children")

    merge_parent = models.ForeignKey('self',
                        null=True, blank=True, default=None,
                        related_name="merge_children")

    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __unicode__(self):
        return u"Id: %r, Tree %r, Parent %r, Patch '''\n%s'''" % (self.id, self.tree_id, self.parent_id, self.patch)

    @staticmethod
    def make_patch(src, dst):
        return pickle.dumps(mdiff.textdiff(src, dst))

    def materialize(self):
        changes = Change.objects.exclude(parent=None).filter(
                        tree=self.tree,
                        created_at__lte=self.created_at).order_by('created_at')
        text = u''
        for change in changes:
            text = change.apply_to(text)
        return text

    def make_child(self, patch, author, description):
        return self.children.create(patch=patch,
                        tree=self.tree, author=author,
                        description=description)

    def make_merge_child(self, patch, author, description):
        return self.merge_children.create(patch=patch,
                        tree=self.tree, author=author,
                        description=description)

    def apply_to(self, text):
        return mdiff.patch(text, pickle.loads(self.patch.encode('ascii')))

    def merge_with(self, other, author, description=u"Automatic merge."):
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
                    author=author, description=description)


class Document(models.Model):
    """
        File in repository.        
    """
    creator = models.ForeignKey(User)
    head = models.ForeignKey(Change,
                    null=True, blank=True, default=None,
                    help_text=_("This document's current head."))

    # Some meta-data
    name = models.CharField(max_length=200,
                help_text=_("Name for this file to display."))

    def __unicode__(self):
        return u"{0}, HEAD: {1}".format(self.name, self.head_id)

    @models.permalink
    def get_absolute_url(self):
        return ('dvcs.views.document_data', (), {
                        'document_id': self.id,
                        'version': self.head_id,
        })

    def materialize(self, version=None):
        if self.head is None:
            return u''
        if version is None:
            version = self.head
        elif not isinstance(version, Change):
            version = self.change_set.get(pk=version)
        return version.materialize()

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
            patch = Change.make_patch(self.materialize(version=parent), kwargs['text'])
        else:
            if 'text' in kwargs:
                raise ValueError("You can provide only text or patch - not both")
            patch = kwargs['patch']

        old_head = self.head
        if parent != old_head:
            change = parent.make_merge_child(patch, kwargs['author'], kwargs.get('description', ''))
            # not Fast-Forward - perform a merge
            self.head = old_head.merge_with(change, author=kwargs['author'])
        else:
            self.head = parent.make_child(patch, kwargs['author'], kwargs.get('description', ''))
        self.save()
        return self.head

    def history(self):
        return self.changes.all()

    @staticmethod
    def listener_initial_commit(sender, instance, created, **kwargs):
        if created:
            instance.head = Change.objects.create(
                    author=instance.creator,
                    patch=pickle.dumps(mdiff.textdiff('', '')),
                    tree=instance)
            instance.save()

models.signals.post_save.connect(Document.listener_initial_commit, sender=Document)
