from django.core.management.base import BaseCommand
from django.db.models import F
from sources.models import Source


class Command(BaseCommand):
    def handle(self, **options):
        for s in Source.objects.exclude(
                modified_at=None
        ).exclude(processed_at__gt=F('modified_at')).order_by('modified_at'):
            print(s)
            try:
                s.process()
            except Exception as e:
                print(e)
                pass

