import json
from django.core.management.base import BaseCommand
from isbn.models import IsbnPool


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename')
    
    def handle(self, filename, **options):
        with open(filename) as f:
            data = json.load(f)
        pool_map = {}
        for d in data:
            f = d['fields']
            if d['model'] == 'isbn.isbnpool':
                pool_map[d['pk']], created = IsbnPool.objects.get_or_create(
                    prefix=f['prefix'],
                    suffix_from=f['suffix_from'],
                    suffix_to=f['suffix_to'],
                    ref_from=f['ref_from'],
                )
            if d['model'] == 'isbn.onixrecord':
                pool = pool_map[f['isbn_pool']]
                isbn, created = pool.isbn_set.get_or_create(
                    suffix=f['suffix'],
                )
                isbn.wl_data = json.dumps(f, indent=4, ensure_ascii=False)
                isbn.save(update_fields=['wl_data'])
