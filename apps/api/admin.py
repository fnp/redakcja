from django.contrib import admin

import api.models

admin.site.register(api.models.PullRequest)
admin.site.register(api.models.PartCache)
