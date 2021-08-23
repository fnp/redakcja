from django.contrib import admin
from . import models


class AttributeInline(admin.TabularInline):
    model = models.Attribute


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = [AttributeInline]
    list_display = ['name', 'type']
    list_filter = ['type']
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'type',
                'similar_to',
                'description',
                'example',
            ]
        }),
        ('Editor style', {
            'fields': [
                'editor_css', 'editor_css_after',
            ]
        }),
    ]



@admin.register(models.TagUsage)
class TagUsageAdmin(admin.ModelAdmin):
    list_filter = ['tag']


@admin.register(models.AttributeUsage)
class AttributeUsageAdmin(admin.ModelAdmin):
    list_filter = ['attribute__tag', 'attribute']
    list_display = ['tag_usage', 'attribute', 'value']
