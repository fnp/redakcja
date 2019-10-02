# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from redakcja.settings.test import *

NOSE_ARGS = ()

STATIC_ROOT_SYMLINK = os.path.dirname(STATIC_ROOT) + '_test'
STATICFILES_DIRS.append(STATIC_ROOT_SYMLINK)
