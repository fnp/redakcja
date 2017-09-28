# -*- coding: utf-8 -*-
from os.path import basename

from django.core.management.base import BaseCommand

from catalogue.xml_tools import wl2_to_wl1


class Command(BaseCommand):
    help = 'Converts a lesson XML from WL2 to WL1'
    args = 'filename'

    def handle(self, filename, *args, **options):
        slug = basename(filename).split('.')[0]
        print wl2_to_wl1(open(filename).read(), slug)
