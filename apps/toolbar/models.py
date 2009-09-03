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
    slug = models.SlugField() #unused

    # behaviour
    params = models.TextField() # TODO: should be a JSON field
    scriptlet = models.ForeignKey('Scriptlet')

    # ui related stuff
    key = models.CharField(blank=True, max_length=1)
    tooltip = models.CharField(blank=True, max_length=120)

    # Why the button is restricted to have the same position in each group ?
    # position = models.IntegerField(default=0)
   
    group = models.ManyToManyField(ButtonGroup)
    
    class Meta:
        ordering = ('label',)
        verbose_name, verbose_name_plural = _('button'), _('buttons')
    
    def __unicode__(self):
        return self.label

class Scriptlet(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    code = models.TextField()

    # TODO: add this later and remap code property to this
    # code_min = models.TextField()

    def __unicode__(self):
        return _(u'javascript')+u':'+self.name
