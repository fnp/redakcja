from contextlib import contextmanager
import os
import shutil
from time import time


@contextmanager
def replace_dir(d):
    # create tmp dir
    d = d.rstrip('/')
    ts = int(time())
    dnew = f'{d}.{ts}.new'
    dold = f'{d}.{ts}.old'
    os.makedirs(dnew)
    try:
        yield dnew
    except:
        shutil.rmtree(dnew)
        raise
    else:
        if os.path.exists(d):
            shutil.move(d, dold)
        shutil.move(dnew, d)
        if os.path.exists(dold):
            shutil.rmtree(dold)
