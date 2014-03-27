from django import template
register = template.Library()


@register.filter
def build_absolute_uri(uri, request):
    return request.build_absolute_uri(uri)

@register.filter
def username(user):
    return ("%s %s" % (user.first_name, user.last_name)).lstrip() or user.username
