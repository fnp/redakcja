from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils.timezone import now
from sources.models import Source


class Command(BaseCommand):
    def handle(self, **options):
        for s in Source.objects.filter(
            modified_at__lt=now() - timedelta(seconds=60)
        ).exclude(processed_at__gt=F('modified_at')).order_by('modified_at'):
            print(s)
            try:
                s.process()
            except Exception as e:
                print(e)
                pass

