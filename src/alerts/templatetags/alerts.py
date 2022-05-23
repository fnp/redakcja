from django.template import Library
from ..models import Alert


register = Library()

@register.simple_tag
def get_alerts():
    return {
        'count': Alert.objects.all().count(),
        'items': Alert.objects.all()[:20],
    }
