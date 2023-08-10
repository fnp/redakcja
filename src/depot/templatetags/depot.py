from django.template import Library
from depot.models import Shop


register = Library()


@register.simple_tag(takes_context=True)
def depot_shops(context, book):
    shops = []
    for shop in Shop.objects.all():
        d = {
            'shop_id': shop.id,
            'name': shop.name,
        }
        d.update(shop.can_publish(book))
        d['last'] = shop.get_last(book)
        d['id'] = getattr(book, shop.shop + '_id')
        shops.append(d)
    return shops
