from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import explorer.models

admin.site.register(explorer.models.EditorSettings)
admin.site.register(explorer.models.EditorPanel)
admin.site.register(explorer.models.PullRequest)
admin.site.register(explorer.models.GalleryForDocument)