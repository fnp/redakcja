# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from .project import Project
from .chunk import Chunk
from .image import Image
from .publish_log import (BookPublishRecord,
    ChunkPublishRecord, ImagePublishRecord)
from .book import Book
from .listeners import *

from django.contrib.auth.models import User as AuthUser


class User(AuthUser):
    class Meta:
        proxy = True

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
