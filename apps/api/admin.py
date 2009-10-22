from django.contrib import admin

from api import models

class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('comitter', 'timestamp', 'comment', 'document', 'source_revision')

admin.site.register(models.PullRequest, PullRequestAdmin)
admin.site.register(models.PartCache)
