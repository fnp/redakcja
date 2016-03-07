from django.utils import translation

from django import template

register = template.Library()


@register.assignment_tag
def flat_lang(page):
    try:
        return type(page).objects.get(url="%s%s/" % (page.url, translation.get_language()))
    except:
        return page

