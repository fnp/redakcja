from celery.task import task
from django.utils import translation
from django.conf import settings


@task
def _refresh_by_pk(cls, pk, language=None):
    prev_language = translation.get_language()
    language and translation.activate(language)
    try:
        cls._default_manager.get(pk=pk).refresh()
    finally:
        translation.activate(prev_language)

def refresh_instance(instance):
    _refresh_by_pk.delay(type(instance), instance.pk, translation.get_language())


@task
def _publishable_error(book, language=None):
    prev_language = translation.get_language()
    language and translation.activate(language)
    try:
        return book.assert_publishable()
    except AssertionError, e:
        return e
    else:
       return None
    finally:
        translation.activate(prev_language)

def publishable_error(book):
    return _publishable_error.delay(book, 
        translation.get_language()).wait()


@task
def book_content_updated(book):
    book.refresh_dc_cache()
