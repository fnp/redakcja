# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.contrib.auth.models import User


class OAuthConnection(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    access = models.BooleanField(default=False)
    token = models.CharField(max_length=64, null=True, blank=True)
    token_secret = models.CharField(max_length=64, null=True, blank=True)
    beta = models.BooleanField(default=False)

    @classmethod
    def get(cls, user, beta=False):
        try:
            return cls.objects.get(user=user, beta=beta)
        except cls.DoesNotExist:
            o = cls(user=user, beta=beta)
            o.save()
            return o
