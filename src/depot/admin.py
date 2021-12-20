from django.contrib import admin
from . import models


@admin.register(models.Package)
class PackageAdmin(admin.ModelAdmin):
    filter_horizontal = ['books']
    pass
    
# Register your models here.
