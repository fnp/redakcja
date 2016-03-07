from __future__ import unicode_literals
from django import template
from forms_builder.forms.models import Form
from forms_builder.forms.forms import EntriesForm

register = template.Library()

@register.assignment_tag(takes_context=True)
def form_count(context, form=None, id=None, slug=None, **kwargs):
    if id is not None:
        form = Form.objects.get(pk=id)
    elif slug is not None:
        form = Form.objects.get(slug=slug)
    ef = EntriesForm(form, context.get('request', None), data=kwargs)
    return sum(1 for i in ef.rows())


@register.assignment_tag(name='set')
def set_tag(sth):
    return sth
