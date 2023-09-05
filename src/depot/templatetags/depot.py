from django.template import Library
from depot.models import Site


register = Library()


@register.simple_tag(takes_context=True)
def depot_sites(context, book):
    sites = []
    for site in Site.objects.all():
        d = {
            'site_id': site.id,
            'name': site.name,
        }
        d.update(site.can_publish(book))
        d['last'] = site.get_last(book)
        d['id'] = site.get_external_id_for_book(book)
        sites.append(d)
    return sites
