from django.template import Library
from django.db.models import Max
from ..models import Alert


register = Library()

@register.simple_tag
def get_alerts():
    return {
        'count': Alert.objects.all().count(),
        'items': Alert.objects.all().annotate(
            m=Max('book__chunk__head__created_at')
        ).order_by('-m')[:20],
    }
