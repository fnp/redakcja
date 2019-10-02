# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.dispatch import Signal

post_commit = Signal()
post_publishable = Signal(providing_args=['publishable'])
