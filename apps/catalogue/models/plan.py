# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from catalogue.models import Document


class Plan(models.Model):
    document = models.ForeignKey(Document)
    stage = models.CharField(max_length=128)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    deadline = models.DateField(null=True, blank=True)
