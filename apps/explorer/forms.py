# -*- coding: utf-8 -*-
from django import forms

from lxml import etree
from librarian import dcparser
import django.utils

from explorer import models

class PersonField(forms.CharField):
    def clean(self, value):
        try:
            return dcparser.Person.from_text( super(PersonField, self).clean(value) )
        except ValueError, e:
            raise django.utils.ValidationError(e.message)

def person_conv(value):
    if isinstance(value, dcparser.Person):
        return value
    elif isinstance(value, basestring):
        return dcparser.Person.from_text( unicode(value) )
    else:
        raise ValueError("Can't convert '%s' to Person object." % value)

class ListField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.convert = kwargs.pop('converter', unicode)
        if not kwargs.has_key('widget'):
            kwargs['widget'] = forms.Textarea
        super(ListField, self).__init__(*args, **kwargs)
    
    def _get_initial(self):
        return self._initial and (u'\n'.join( ( unicode(person) for person in self._initial)))

    def _set_initial(self, value):
        if value is None:
            self._initial = None
        elif isinstance(value, list):
            self._initial = [ self.convert(e) for e in value ]
        elif isinstance(value, basestring):
            self._initial = [ self.convert(e) for e in value.split('\n') ]
        else:
            raise ValueError("Invalid value. Must be a list of dcparser.Person or string")    

    initial = property(_get_initial, _set_initial)

    def clean(self, value):
        super(ListField, self).clean(value)
        elems = value.split('\n')
        try:
            return [self.convert(el) for el in elems]
        except ValueError, err:
            raise django.utils.ValidationError(err.message)

class BookForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
    commit_message = forms.CharField(required=False)

class MergeForm(forms.Form):
    message = forms.CharField(error_messages={'required': 'Please write a merge description.'})

class BookUploadForm(forms.Form):
    file = forms.FileField(label='Source OCR file')
    bookname = forms.RegexField(regex='[0-9\w_-]+',  \
        label='Publication name', help_text='Example: slowacki-beniowski')
    autoxml = forms.BooleanField(required=False, initial=True, label=u"Generate DublinCore template")

class ImageFoldersForm(forms.Form):
    folders = forms.ChoiceField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ImageFoldersForm, self).__init__(*args, **kwargs)
        self.fields['folders'].choices = [('', '-- Wybierz folder z obrazkami --')] + [(fn, fn) for fn in models.get_image_folders()]

class SplitForm(forms.Form):
    partname = forms.RegexField(regex='[0-9\w_-]+',  \
        label='Part name', help_text='Example: rozdział-2')
    autoxml = forms.BooleanField(required=False, initial=False, label=u"Split as new publication")
    fulltext = forms.CharField(widget=forms.HiddenInput(), required=False)
    splittext = forms.CharField(widget=forms.HiddenInput(), required=False)

class DublinCoreForm(forms.Form):
    about = forms.URLField(verify_exists=False)
    author = PersonField()
    title = forms.CharField()
    epochs = ListField()
    kinds = ListField()
    genres = ListField()
    created_at = forms.DateField()
    released_to_public_domain_at = forms.DateField(required=False)
    editors = ListField(widget=forms.Textarea, required=False, converter=person_conv)
    translators = ListField(widget=forms.Textarea, required=False, converter=person_conv)
    technical_editors = ListField(widget=forms.Textarea, required=False, converter=person_conv)
    publisher = forms.CharField()
    source_name = forms.CharField(widget=forms.Textarea, required=False)
    source_url = forms.URLField(verify_exists=False, required=False)
    url = forms.URLField(verify_exists=False)
    parts = forms.CharField(widget=forms.Textarea, required=False)
    license = forms.CharField(required=False)
    license_description = forms.CharField(widget=forms.Textarea, required=False)
    
    commit_message = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        info = kwargs.pop('info', None)        
        super(DublinCoreForm, self).__init__(*args, **kwargs)
        
        if isinstance(info, dcparser.BookInfo):
            vdict = info.to_dict()
            for name in self.fields.keys():
                if vdict.has_key(name):
                    self.fields[name].initial = vdict[name]