# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import unicode_literals

from django.dispatch import Signal

post_commit = Signal(providing_args=['instance'])
post_merge = Signal(providing_args=['fast_forward', 'instance'])
