# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from celery.task import task
from django.utils import translation


@task(ignore_result=True)
def _refresh_by_pk(cls, pk, language=None):
    prev_language = translation.get_language()
    language and translation.activate(language)
    try:
        cls._default_manager.get(pk=pk).refresh()
    finally:
        translation.activate(prev_language)


def refresh_instance(instance):
    _refresh_by_pk.delay(type(instance), instance.pk, translation.get_language())


@task(ignore_result=True)
def book_content_updated(book):
    book.refresh_dc_cache()
