from django.contrib.admin import site
from dvcs.models import Document, Change

site.register(Document)
site.register(Change)
