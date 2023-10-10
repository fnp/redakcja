from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE)
    presence = models.BooleanField()
    approve_by_default = models.BooleanField()

    class Meta:
        verbose_name = verbose_name_plural = 'profil'

    def __str__(self):
        return self.user.username


class Presence(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    chunk = models.ForeignKey('documents.Chunk', models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    active = models.BooleanField()

    @classmethod
    def report(cls, user, chunk, active):
        if user.is_anonymous or not hasattr(user, 'profile') or not user.profile.presence:
            return
        cls.objects.create(
            user=user,
            chunk=chunk,
            timestamp=now(),
            active=active
        )
