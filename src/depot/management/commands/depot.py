from django.core.management.base import BaseCommand
from depot.models import ShopBookPublish


class Command(BaseCommand):
    def handle(self, **options):
        for p in ShopBookPublish.objects.filter(status=0).order_by('created_at'):
            print(p.id, p.shop, p.book.slug, p.created_at)
            p.publish()

