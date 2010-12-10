# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from dvcs.models import Document


class ImageDocument(models.Model):
    slug = models.SlugField(_('slug'), max_length=120)
    name = models.CharField(_('name'), max_length=120)
    image = models.ImageField(_('image'), upload_to='wiki_img')
    doc = models.OneToOneField(Document, null=True, blank=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    @staticmethod
    def listener_initial_commit(sender, instance, created, **kwargs):
        if created:
            instance.doc = Document.objects.create(creator=instance.creator)
            instance.save()

    def __unicode__(self):
        return self.name


models.signals.post_save.connect(ImageDocument.listener_initial_commit, sender=ImageDocument)
