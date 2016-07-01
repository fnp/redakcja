# -*- coding: utf-8 -*-
"""
    Mercurial ui module replacement.
"""

import mercurial.ui
import logging


class SilentUI(mercurial.ui.ui):

    def __init__(self, *args, **kwargs):
        super(SilentUI, self).__init__(*args, **kwargs)

        # make sure this doesn't collide with anything in Mercurial
        self.__logger = logging.getLogger('mercurial')

    def _is_trusted(self, fd, filename):
        """ Checks if config file is trusted - on server side, this isn't very useful. """
        return True

    def write(self, *args):
        if self._buffers:
            self._buffers[-1].extend([str(a) for a in args])
        else:
            self.__logger.info(''.join(args))

    def write_err(self, *args):
        self.__logger.error(''.join(args))

    def flush(self):
        pass

    def interactive(self):
        return False

    def _readline(self, prompt=''):
        return u''

    def status(self, *msg):
        self.__logger.debug(''.join(msg))

    def warn(self, *msg):
        self.__logger.warn(''.join(msg))

    def note(self, *msg):
        self.__logger.info(''.join(msg))

    def debug(self, *msg):
        self.__logger.debug(''.join(msg))

    def edit(self, text, user):
        return text

    def traceback(self, exc=None):
        if exc is not None:
            self.__logger.exception()

    def progress(self, *args, **kwargs):
        pass
