from redakcja.settings.test import *

NOSE_ARGS = ()

STATIC_ROOT_SYMLINK = os.path.dirname(STATIC_ROOT) + '_test'
STATICFILES_DIRS.append(STATIC_ROOT_SYMLINK)

