# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from django.db import models
from catalogue.models import Book, Chunk
from catalogue.signals import post_publish
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


def user_changed(sender, instance, *args, **kwargs):
    books = set()
    for c in instance.chunk_set.all():
        books.add(c.book)
        c.touch()
    for b in books:
        b.touch()
models.signals.post_save.connect(user_changed, sender=User)


def publish_listener(sender, *args, **kwargs):
    sender.book.touch()
    for c in sender.book:
        c.touch()
post_publish.connect(publish_listener)


def publishable_listener(sender, *args, **kwargs):
    sender.tree.touch()
    sender.tree.book.touch()
post_publishable.connect(publishable_listener)


def listener_create(sender, instance, created, **kwargs):
    if created:
        instance.chunk_set.create(number=1, slug='1')
models.signals.post_save.connect(listener_create, sender=Book)
