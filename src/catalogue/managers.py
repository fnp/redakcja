# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models

class VisibleManager(models.Manager):
    def get_queryset(self):
        return super(VisibleManager, self).get_queryset().exclude(_hidden=True)
