from datetime import timedelta
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
    GAP_THRESHOLD = 10

    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255)
    chunk = models.ForeignKey('documents.Chunk', models.SET_NULL, blank=True, null=True)
    since = models.DateTimeField(auto_now_add=True, db_index=True)
    until = models.DateTimeField(db_index=True)
    active = models.BooleanField()

    @classmethod
    def report(cls, user, session_key, chunk, active):
        user = user if not user.is_anonymous else None
        report = cls.objects.filter(
            user=user,
            session_key=session_key,
            chunk=chunk,
            until__gt=now() - timedelta(seconds=cls.GAP_THRESHOLD)
        ).order_by('-until').first()
        if report is None or report.active != active:
            report = cls.objects.create(
                user=user,
                session_key=session_key,
                chunk=chunk,
                active=active,
                until=now(),
            )
        else:
            report.until = now()
            report.save()

    @classmethod
    def get_current(cls, session_key, chunk):
        sessions = set()
        presences = []
        for p in cls.objects.filter(
            chunk=chunk,
            until__gt=now() - timedelta(seconds=cls.GAP_THRESHOLD)
        ).exclude(session_key=session_key).order_by('-since'):
            if p.session_key not in sessions:
                sessions.add(p.session_key)
                presences.append(p)
        presences.reverse()
        return presences
