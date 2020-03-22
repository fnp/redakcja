# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from django.db import models
from documents.models import (Book, Chunk, Image, BookPublishRecord,
        ImagePublishRecord)
from documents.signals import post_publish
from dvcs.signals import post_publishable


def book_changed(sender, instance, created, **kwargs):
    instance.touch()
    for c in instance:
        c.touch()
models.signals.post_save.connect(book_changed, sender=Book)


def chunk_changed(sender, instance, created, **kwargs):
    instance.book.touch()
    instance.touch()
models.signals.post_save.connect(chunk_changed, sender=Chunk)


def image_changed(sender, instance, created, **kwargs):
    instance.touch()
models.signals.post_save.connect(image_changed, sender=Image)


def publish_listener(sender, *args, **kwargs):
    if isinstance(sender, BookPublishRecord):
        sender.book.touch()
        for c in sender.book:
            c.touch()
    elif isinstance(sender, ImagePublishRecord):
        sender.image.touch()
post_publish.connect(publish_listener)


def chunk_publishable_listener(sender, *args, **kwargs):
    sender.tree.touch()
    if isinstance(sender.tree, Chunk):
        sender.tree.book.touch()
post_publishable.connect(chunk_publishable_listener)

def publishable_listener(sender, *args, **kwargs):
    sender.tree.touch()
post_publishable.connect(publishable_listener, sender=Image)


def listener_create(sender, instance, created, **kwargs):
    if created:
        instance.chunk_set.create(number=1, slug='1')
models.signals.post_save.connect(listener_create, sender=Book)

