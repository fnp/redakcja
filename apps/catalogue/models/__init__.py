# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue.models.template import Template
from catalogue.models.document import Document
from catalogue.models.plan import Plan
from catalogue.models.publish_log import PublishRecord
from catalogue.models.tag import Category, Tag

from django.contrib.auth.models import User as AuthUser


class User(AuthUser):
    class Meta:
        proxy = True

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)
