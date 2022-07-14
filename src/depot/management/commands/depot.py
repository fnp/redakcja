from django.core.management.base import BaseCommand
from depot.models import LegimiBookPublish


class Command(BaseCommand):
    def handle(self, **options):
        for p in LegimiBookPublish.objects.filter(status=0).order_by('created_at'):
            print(p, p.book.slug, p.created_at)
            p.publish()

