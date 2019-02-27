from django.dispatch import Signal

post_commit = Signal()
post_publishable = Signal(providing_args=['publishable'])
