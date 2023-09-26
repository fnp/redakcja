from django.contrib import admin
from . import models

@admin.register(models.Isbn)
class IsbnAdmin(admin.ModelAdmin):
    search_fields = ['pool__prefix', 'suffix']


admin.site.register(models.IsbnPool)

# Register your models here.
