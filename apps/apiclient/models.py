# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class OAuthConnection(models.Model):
    user = models.OneToOneField(User)
    access = models.BooleanField(default=False)
    token = models.CharField(max_length=64, null=True, blank=True)
    token_secret = models.CharField(max_length=64, null=True, blank=True)

    @classmethod
    def get(cls, user):
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            o = cls(user=user)
            o.save()
            return o
