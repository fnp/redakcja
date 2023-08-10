from admin_ordering.admin import OrderableAdmin
from django.contrib import admin
from . import models


@admin.register(models.Package)
class PackageAdmin(admin.ModelAdmin):
    raw_id_fields = ['books']


class MediaInsertTextInline(OrderableAdmin, admin.TabularInline):
    model = models.MediaInsertText
    extra = 0


class PriceLevelInline(OrderableAdmin, admin.TabularInline):
    model = models.PriceLevel
    extra = 0


@admin.register(models.Shop)
class ShopAdmin(admin.ModelAdmin):
    inlines = [
        MediaInsertTextInline,
        PriceLevelInline,
    ]
