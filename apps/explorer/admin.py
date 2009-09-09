from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import explorer.models

admin.site.register(explorer.models.EditorSettings)
admin.site.register(explorer.models.Book)
admin.site.register(explorer.models.EditorPanel)