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

class KeyModSelector(forms.MultiWidget):
    def __init__(self):
        super(KeyModSelector, self).__init__(
            [forms.CheckboxInput() for x in xrange(0,3)])

    def decompress(self, v):
        if not v: v = 0
        r = [(v&0x01) != 0, (v&0x02) != 0, (v&0x04) != 0]
        print "DECOMPRESS: " , v, repr(r)
        return r

    def format_output(self, widgets):
        out = u''
        out += u'<p>' + widgets[0] + u' Alt </p>'
        out += u'<p>' + widgets[1] + u' Ctrl </p>'
        out += u'<p>' + widgets[2] + u' Shift </p>'
        return out

class KeyModField(forms.MultiValueField):

    def __init__(self):
        super(KeyModField, self).__init__(\
            fields=tuple(forms.BooleanField() for x in xrange(0,3)), \
            widget=KeyModSelector() )

    def compress(self, dl):
        v = int(dl[0]) | (int(dl[1]) << 1) | (int(dl[2]) << 2)
        print "COMPRESS", v
        return v
    

class ButtonAdminForm(forms.ModelForm):
    key_mod = KeyModField()

    class Meta:
        model = models.Button

    def clean_params(self):
        value = self.cleaned_data['params']
        try:
            return json.dumps(json.loads(value))
        except Exception, e:
            raise forms.ValidationError(e)



class ButtonAdmin(admin.ModelAdmin):
    form = ButtonAdminForm
    list_display = ('label', 'scriptlet', 'hotkey_name', 'params')
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

