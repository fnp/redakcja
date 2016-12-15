# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import unicode_literals, print_function

from datetime import datetime
import os
import re
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from dvcs.signals import post_commit, post_merge
from dvcs.storage import GzipFileSystemStorage

# default repository path; make a setting for it
REPO_PATH = os.path.join(settings.MEDIA_ROOT, 'dvcs')
repo = GzipFileSystemStorage(location=REPO_PATH)


@python_2_unicode_compatible
class Revision(models.Model):
    """
    A document revision. The "parent"
    argument points to the version against which this change has been 
    recorded. Initial text will have a null parent.

    Gzipped text of the document is stored in a file.
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name=_('author'))
    author_name = models.CharField(
        _('author name'), max_length=128, null=True, blank=True, help_text=_("Used if author is not set."))
    author_email = models.CharField(
        _('author email'), max_length=128, null=True, blank=True, help_text=_("Used if author is not set."))
    # Any other author data?
    # How do we identify an author?

    parent = models.ForeignKey(
        'self', null=True, blank=True, default=None, verbose_name=_('parent'), related_name="children")

    merge_parent = models.ForeignKey(
        'self', null=True, blank=True, default=None, verbose_name=_('merge parent'), related_name="merge_children")

    description = models.TextField(_('description'), blank=True, default='')
    created_at = models.DateTimeField(editable=False, db_index=True, default=datetime.now)

    class Meta:
        ordering = ('created_at',)
        verbose_name = _("revision")
        verbose_name_plural = _("revisions")

    def __str__(self):
        return "Id: %r, Parent %r, Data: %s" % (self.id, self.parent_id, self.get_text_path())

    def get_text_path(self):
        if self.pk:
            return re.sub(r'([0-9a-f]{2})([^.])', r'\1/\2', '%x.gz' % self.pk)
        else:
            return None

    def save_text(self, content):
        return repo.save(self.get_text_path(), ContentFile(content.encode('utf-8')))

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

    @classmethod
    def create(cls, text, parent=None, merge_parent=None, author=None, author_name=None, author_email=None,
               description=''):

        if text:
            text = text.replace(
                '<dc:></dc:>', '').replace(
                '<div class="img">', '<div>')

        revision = cls.objects.create(
            parent=parent,
            merge_parent=merge_parent,
            author=author,
            author_name=author_name,
            author_email=author_email,
            description=description
        )
        revision.save_text(text)
        return revision

    def materialize(self):
        f = repo.open(self.get_text_path())
        text = f.read().decode('utf-8')
        f.close()
        if text:
            text = text.replace(
                '<dc:></dc:>', '').replace(
                '<div class="img">', '<div>')
        return text

    def is_descendant_of(self, other):
        # Naive approach.
        return (
            (
                self.parent is not None and (
                    self.parent.pk == other.pk or
                    self.parent.is_descendant_of(other)
                )
            ) or (
                self.merge_parent is not None and (
                    self.merge_parent.pk == other.pk or
                    self.merge_parent.is_descendant_of(other)
                )
            )
        )

    def get_common_ancestor_with(self, other):
        # VERY naive approach.
        if self.pk == other.pk:
            return self
        if self.is_descendant_of(other):
            return other
        if other.is_descendant_of(self):
            return self

        if self.parent is not None:
            parent_ca = self.parent.get_common_ancestor_with(other)
        else:
            parent_ca = None

        if self.merge_parent is not None:
            merge_parent_ca = self.merge_parent.get_common_ancestor_with(other)
        else:
            return parent_ca

        if parent_ca is None or parent_ca.created_at < merge_parent_ca.created_at:
            return merge_parent_ca

        return parent_ca

    def get_ancestors(self):
        revs = set()
        if self.parent is not None:
            revs.add(self.parent)
            revs.update(self.parent.get_ancestors())
        if self.merge_parent is not None:
            revs.add(self.merge_parent)
            revs.update(self.merge_parent.get_ancestors())
        return revs


@python_2_unicode_compatible
class Ref(models.Model):
    """A reference pointing to a specific revision."""

    revision = models.ForeignKey(
        Revision, null=True, blank=True, default=None, verbose_name=_('revision'),
        help_text=_("The document's revision."), editable=False)

    def __str__(self):
        return "ref:{0}->rev:{1}".format(self.id, self.revision_id)

    def merge_text(self, base, local, remote):
        """Override in subclass to have different kinds of merges."""
        files = []
        for f in local, base, remote:
            temp = NamedTemporaryFile(delete=False)
            temp.write(f)
            temp.close()
            files.append(temp.name)
        p = Popen(['/usr/bin/diff3', '-mE', '-L', 'old', '-L', '', '-L', 'new'] + files, stdout=PIPE)
        result, errs = p.communicate()

        for f in files:
            os.unlink(f)
        return result.decode('utf-8')

    def merge_with(self, revision, author=None, author_name=None, author_email=None, description="Automatic merge."):
        """Merges a given revision into the ref."""
        if self.revision is None:
            fast_forward = True
            self.revision = revision
        elif self.revision.pk == revision.pk or self.revision.is_descendant_of(revision):
            # Already merged.
            return
        elif revision.is_descendant_of(self.revision):
            # Fast forward.
            fast_forward = True
            self.revision = revision
        else:
            # Need to create a merge revision.
            fast_forward = False
            base = self.revision.get_common_ancestor_with(revision)

            local_text = self.materialize().encode('utf-8')
            base_text = base.materialize().encode('utf-8')
            other_text = revision.materialize().encode('utf-8')

            merge_text = self.merge_text(base_text, local_text, other_text)

            merge_revision = Revision.create(
                text=merge_text,
                parent=self.revision,
                merge_parent=revision,
                author=author,
                author_name=author_name,
                author_email=author_email,
                description=description
            )
            self.revision = merge_revision
        self.save()
        post_merge.send(sender=type(self), instance=self, fast_forward=fast_forward)

    def materialize(self):
        return self.revision.materialize() if self.revision is not None else ''

    def commit(self, text, parent=False, author=None, author_name=None, author_email=None, description=''):
        """Creates a new revision and sets it as the ref.

        This will automatically merge the commit into the main branch,
        if parent is not document's head.

        :param unicode text: new version of the document
        :param User author: the commiter
        :param unicode author_name: commiter name (if ``author`` not specified)
        :param unicode author_email: commiter e-mail (if ``author`` not specified)
        :returns: new head
        """
        if parent is False:
            # If parent revision not set explicitly, use your head.
            parent = self.revision

        # Warning: this will silently leave revs unreferenced.
        rev = Revision.create(
                text=text,
                author=author,
                author_name=author_name,
                author_email=author_email,
                description=description,
                parent=parent
            )
        self.merge_with(rev, author=author, author_name=author_name, author_email=author_email)

        post_commit.send(sender=type(self), instance=self)

    def history(self):
        revs = self.revision.get_ancestors()
        revs.add(self.revision)
        return sorted(revs, key=lambda x: x.created_at)
