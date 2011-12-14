from datetime import date
from functools import wraps

from django.db.models import Count


def active_tab(tab):
    """
        View decorator, which puts tab info on a request.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(request, *args, **kwargs):
            request.catalogue_active_tab = tab
            return f(request, *args, **kwargs)
        return wrapped
    return wrapper


def cached_in_field(field_name):
    def decorator(f):
        @property
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            value = getattr(self, field_name)
            if value is None:
                value = f(self, *args, **kwargs)
                type(self)._default_manager.filter(pk=self.pk).update(**{field_name: value})
            return value
        return wrapped
    return decorator


def parse_isodate(isodate):
    try:
        return date(*[int(p) for p in isodate.split('-')])
    except (AttributeError, TypeError, ValueError):
        raise ValueError("Not a date in ISO format.")
