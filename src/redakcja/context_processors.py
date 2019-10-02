# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
def settings(request):
    from django.conf import settings

    if settings.SHOW_APP_VERSION:
        import subprocess
        process = subprocess.Popen(["git", "show", "--oneline"], stdout=subprocess.PIPE)
        data, _err = process.communicate()
        # get app version
        VERSION = data.splitlines()[0].split()[0]
    else:
        VERSION = ''

    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'APP_VERSION': VERSION,
    }
