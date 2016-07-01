# -*- coding: utf-8 -*-
from django.db import models


class VisibleManager(models.Manager):
    def get_query_set(self):
        return super(VisibleManager, self).get_query_set().exclude(_hidden=True)
