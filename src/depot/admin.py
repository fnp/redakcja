from django.contrib import admin
from . import models


@admin.register(models.Package)
class PackageAdmin(admin.ModelAdmin):
    raw_id_fields = ['books']
