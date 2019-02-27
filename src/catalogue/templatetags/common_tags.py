from django import template
register = template.Library()

@register.filter
def username(user):
    return ("%s %s" % (user.first_name, user.last_name)).lstrip() or user.username
