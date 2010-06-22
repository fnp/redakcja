from django.contrib.admin import site
from dcmeta.models import Description, Attr, Schema

site.register(Description)
site.register(Attr)
site.register(Schema)
