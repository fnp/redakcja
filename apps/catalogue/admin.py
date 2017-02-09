# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from catalogue import models

admin.site.register(models.Document)
admin.site.register(models.Template)

admin.site.register(models.Category)
admin.site.register(models.Tag)
