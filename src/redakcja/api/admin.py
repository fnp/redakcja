from django.contrib import admin
from . import models


@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
    readonly_fields = ['key', 'created', 'last_seen_at']
