from django.contrib import admin

from catalogue import models

admin.site.register(models.Document)
admin.site.register(models.Template)
