from django.db import models

class VisibleManager(models.Manager):
    def get_queryset(self):
        return super(VisibleManager, self).get_queryset().exclude(_hidden=True)
