from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.
class Theme(models.Model):
    name = models.CharField(name=_("Name"), max_length=64, primary_key=True)
    description = models.TextField(name=_("Description"), blank=True)

    class Meta:
        verbose_name, verbose_name_plural = (_("theme"), _("themes"))

    def __unicode__(self):
        return self.name