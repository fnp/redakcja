# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    help = 'Exports a lesson in WL1 XML'
    args = 'slug'
    option_list = BaseCommand.option_list + (
        make_option(
            '-c', '--current', action='store_false', dest='publishable', default=True,
            help='Current version (even if not publishable)'),
    )

    def handle(self, slug, *args, **options):
        lesson = Book.objects.get(slug=slug)
        print lesson.wl1_xml(publishable=options.get('publishable'))
