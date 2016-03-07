from __future__ import unicode_literals

from django.dispatch import Signal

post_commit = Signal(providing_args=['instance'])
post_merge = Signal(providing_args=['fast_forward', 'instance'])