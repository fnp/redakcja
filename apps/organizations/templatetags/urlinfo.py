from django import template
from embeder import embed

register = template.Library()

@register.assignment_tag
def urlinfo(url):
    try:
        return embed.get(url).get('global', {})
    except:
        return {}
