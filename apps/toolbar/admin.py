from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.utils import simplejson as json

from toolbar import models

#class ButtonGroupAdmin(admin.ModelAdmin):
#    list_display = ('name', 'slug', 'position',)
#    search_fields = ('name', 'slug',)
#    prepopulated_fields = {'slug': ('name',)}
#    list_editable = ('position',)


class ButtonAdminForm(forms.ModelForm):
    model = models.Button

    def clean_params(self):
        value = self.cleaned_data['params']
        try:
            return json.dumps(json.loads(value))
        except Exception, e:
            raise forms.ValidationError(e)

class ButtonAdmin(admin.ModelAdmin):
    form = ButtonAdminForm
    list_display = ('label', 'scriptlet', 'key', 'params')
    prepopulated_fields = {'slug': ('label',)}

admin.site.register(models.Button, ButtonAdmin)
admin.site.register(models.ButtonGroup)
admin.site.register(models.Scriptlet)

#class ButtonAdmin(admin.ModelAdmin):
#    list_display = ('label', 'action', 'key', 'position',)
#    list_filter = ('group',)
#    search_fields = ('label', 'action', 'key',)
#    filter_horizontal = ('group',)
#    list_editable = ('position',)

