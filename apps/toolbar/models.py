from django.db import models
from django.utils.translation import ugettext_lazy as _


class ButtonGroup(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField()
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('position', 'name',)
        verbose_name, verbose_name_plural = _('button group'), _('button groups')
    
    def __unicode__(self):
        return self.name


class Button(models.Model):
    label = models.CharField(max_length=32)
    slug = models.SlugField()
    tag = models.CharField(max_length=128)
    key = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(default=0)
    
    group = models.ManyToManyField(ButtonGroup)
    
    class Meta:
        ordering = ('position', 'label',)
        verbose_name, verbose_name_plural = _('button'), _('buttons')
    
    def __unicode__(self):
        return self.label

