from django.db import models


class Template(models.Model):
    """ Template of a document or its part """
    
    name = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        app_label = 'catalogue'

    def __unicode__(self):
        return self.name
