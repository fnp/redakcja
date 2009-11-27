from django.conf import settings

if not hasattr(settings, 'WIKI_REPOSITORY_PATH'):
    raise Exception('You must set WIKI_REPOSITORY_PATH in your settings file.')

REPOSITORY_PATH = settings.WIKI_REPOSITORY_PATH
