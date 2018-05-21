# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from constance import config
from django.core.mail import send_mail


def send_notify_email(subject, content):
    addresses = [part.strip() for part in config.NOTIFY_EMAIL.split(';') if '@' in part]
    send_mail(subject, content, 'milpeer@mdrn.pl', addresses)
