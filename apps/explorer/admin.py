from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from explorer import models

admin.site.register(models.Book)
admin.site.register(models.PullRequest)

