# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    help = 'Exports a lesson in WL1 XML'
    args = 'slug'

    def handle(self, slug, *args, **options):
        lesson = Book.objects.get(slug=slug)
        print lesson.wl1_xml()