from django.contrib import admin
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'presence']


@admin.register(models.Presence)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp', 'active']

