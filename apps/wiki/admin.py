from django.contrib import admin

from wiki import models

class ThemeAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(models.Theme, ThemeAdmin)
