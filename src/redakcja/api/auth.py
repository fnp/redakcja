from django.utils.timezone import now
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from . import models


class TokenAuthentication(BaseTokenAuthentication):
    model = models.Token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        token.last_seen_at = now()
        token.save(update_fields=['last_seen_at'])
        return (user, token)
