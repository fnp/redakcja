from django.contrib.admin import site
from dvcs.models import Document, Change, Tag

site.register(Tag)
site.register(Document)
site.register(Change)
