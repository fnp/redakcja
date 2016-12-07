# -*- coding: utf-8 -*-
from django.contrib import admin

from attachments.models import Attachment


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('key',)
    search_fields = ('key',)

admin.site.register(Attachment, AttachmentAdmin)
