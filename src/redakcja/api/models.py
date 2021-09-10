from django.conf import settings
from django.db import models
from rest_framework.authtoken.models import Token as TokenBase


class Token(TokenBase):
    last_seen_at = models.DateTimeField(blank=True, null=True)
    api_version = models.IntegerField(choices=[
        (1, '1'),
    ])
