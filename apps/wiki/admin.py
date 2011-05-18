from django.contrib import admin

from wiki import models

admin.site.register(models.Book)
admin.site.register(models.Theme)
