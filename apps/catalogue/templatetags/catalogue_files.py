from django import template
from django.conf import settings
register = template.Library()


@register.filter
def as_media_for(uri, document):
    if uri.startswith('file://'):
        uri = "https://milpeer.eu%suploads/%d/%s" % (settings.MEDIA_URL, document.pk, uri[len('file://'):])
    return uri

