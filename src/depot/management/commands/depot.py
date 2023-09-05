from django.core.management.base import BaseCommand
from depot.models import SiteBookPublish


class Command(BaseCommand):
    def handle(self, **options):
        for p in SiteBookPublish.objects.filter(status=0).order_by('created_at'):
            print(p.id, p.site_book, p.created_at)
            p.publish()

