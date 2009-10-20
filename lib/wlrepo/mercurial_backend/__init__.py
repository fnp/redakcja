# -*- encoding: utf-8 -*-

import logging
log = logging.getLogger('ral.mercurial')

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-25 09:20:22$"
__doc__ = "Module documentation."

import wlrepo


from mercurial import encoding
encoding.encoding = 'utf-8'