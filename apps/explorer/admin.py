from django.contrib import admin

import explorer.models

admin.site.register(explorer.models.EditorSettings)
admin.site.register(explorer.models.EditorPanel)
admin.site.register(explorer.models.GalleryForDocument)