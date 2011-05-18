# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dvcs import models as dvcs_models


import logging
logger = logging.getLogger("fnp.wiki")


class Book(models.Model):
    """ A document edited on the wiki """

    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    title = models.CharField(_('displayed title'), max_length=255, blank=True)
    doc = models.ForeignKey(dvcs_models.Document, editable=False)
    gallery = models.CharField(_('scan gallery name'), max_length=255, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __unicode__(self):
        return self.title

    @classmethod
    def create(cls, creator=None, text=u'', *args, **kwargs):
        instance = cls(*args, **kwargs)
        instance.doc = dvcs_models.Document.create(creator=creator, text=text)
        instance.save()
        return instance

    @staticmethod
    def listener_create(sender, instance, created, **kwargs):
        if created and instance.doc is None:
            instance.doc = dvcs_models.Document.objects.create()
            instance.save()

models.signals.post_save.connect(Book.listener_create, sender=Book)



'''
from wiki import settings, constants
from slughifi import slughifi

from django.http import Http404




class Document(object):

    def add_tag(self, tag, revision, author):
        """ Add document specific tag """
        logger.debug("Adding tag %s to doc %s version %d", tag, self.name, revision)
        self.storage.vstorage.add_page_tag(self.name, revision, tag, user=author)

    @property
    def plain_text(self):
        return re.sub(self.META_REGEX, '', self.text, 1)

    def meta(self):
        result = {}

        m = re.match(self.META_REGEX, self.text)
        if m:
            for line in m.group(1).split('\n'):
                try:
                    k, v = line.split(':', 1)
                    result[k.strip()] = v.strip()
                except ValueError:
                    continue

        gallery = result.get('gallery', slughifi(self.name.replace(' ', '_')))

        if gallery.startswith('/'):
            gallery = os.path.basename(gallery)

        result['gallery'] = gallery
        return result

    def info(self):
        return self.storage.vstorage.page_meta(self.name, self.revision)



'''
class Theme(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('theme')
        verbose_name_plural = _('themes')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Theme(name=%r)" % self.name

