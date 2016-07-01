# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue.models.template import Template
from catalogue.models.project import Project
from catalogue.models.chunk import Chunk
from catalogue.models.publish_log import BookPublishRecord, ChunkPublishRecord
from catalogue.models.book import Book
from catalogue.models.listeners import *

from django.contrib.auth.models import User as AuthUser


class User(AuthUser):
    class Meta:
        proxy = True

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)
