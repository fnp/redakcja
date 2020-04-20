# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import defaultdict
from django.db.models import QuerySet
from django.db.models.manager import BaseManager


class UnrelatedQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prefetch_unrelated_lookups = {}
        self._prefetch_unrelated_done = False

    def _clone(self):
        c = super()._clone()
        c._prefetch_unrelated_lookups = self._prefetch_unrelated_lookups.copy()
        return c

    def prefetch_unrelated(self, attribute, field, other_model, other_field):
        clone = self._clone()
        clone._prefetch_unrelated_lookups[field] = (attribute, other_model, other_field)
        return clone

    def _fetch_all(self):
        prefetch_done = self._prefetch_done
        super()._fetch_all()
        if self._prefetch_unrelated_lookups and not prefetch_done:
            self._prefetch_unrelated_objects()

    def _prefetch_unrelated_objects(self):
        for (
            field,
            (attribute, other_model, other_field),
        ) in self._prefetch_unrelated_lookups.items():
            values = set([getattr(obj, field) for obj in self._result_cache])
            other_objects = other_model._default_manager.filter(
                **{f"{other_field}__in": values}
            )
            results = defaultdict(list)
            for other_obj in other_objects:
                results[getattr(other_obj, other_field)].append(other_obj)
            for obj in self._result_cache:
                setattr(obj, attribute, results.get(getattr(obj, field)))
        self._prefetch_unrelated_done = True


class UnrelatedManager(BaseManager.from_queryset(UnrelatedQuerySet)):
    pass
