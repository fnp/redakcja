# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from wiki import models


class ThemeAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(models.Theme, ThemeAdmin)
