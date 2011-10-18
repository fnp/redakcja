from celery.task import task


@task
def refresh_by_pk(cls, pk):
    cls._default_manager.get(pk=pk).refresh()


def refresh_instance(instance):
    refresh_by_pk.delay(type(instance), instance.pk)


@task
def publishable_error(book):
    try:
        book.assert_publishable()
    except AssertionError, e:
        return e
    else:
       return None
