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

class PersonListField(forms.Field):

    def __init__(self, *args, **kwargs):
        super(PersonListField, self).__init__(*args, **kwargs)
    
    def _get_initial(self):
        return self._initial and (u'\n'.join( ( unicode(person) for person in self._initial)))

    def _set_initial(self, value):
        if value is None:
            self._initial = None
        elif isinstance(value, list):
            self._initial = [ e if isinstance(e, dcparser.Person) \
                else dcparser.Person.from_text(e) for e in value ]
        elif isinstance(value, basestring):
            self._initial = [dcparser.Person.from_text(token) for token in value.split('\n') ]
        else:
            raise ValueError("Invalid value. Must be a list of dcparser.Person or string")    

    initial = property(_get_initial, _set_initial)

    def clean(self, value):
        super(PersonListField, self).clean(value)
        people = value.split('\n')
        try:
            return [dcparser.Person.from_text(person) for person in people]
        except ValueError, e:
            raise django.utils.ValidationError(e.message)        

class BookForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
    commit_message = forms.CharField(required=False)

class BookUploadForm(forms.Form):
    file = forms.FileField()

class ImageFoldersForm(forms.Form):
    folders = forms.ChoiceField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ImageFoldersForm, self).__init__(*args, **kwargs)
        self.fields['folders'].choices = [('', '-- Wybierz folder z obrazkami --')] + [(fn, fn) for fn in models.get_image_folders()]


class DublinCoreForm(forms.Form):
    about = forms.URLField(verify_exists=False)
    author = PersonField()
    title = forms.CharField()
    epoch = forms.CharField()
    kind = forms.CharField()
    genre = forms.CharField()
    created_at = forms.DateField()
    released_to_public_domain_at = forms.DateField()
    editors = PersonListField(widget=forms.Textarea, required=False)
    translator = PersonField(required=False)
    technical_editor = PersonField(required=False)
    publisher = PersonField()
    source_name = forms.CharField(widget=forms.Textarea)
    source_url = forms.URLField(verify_exists=False)
    url = forms.URLField(verify_exists=False)
    parts = forms.CharField(widget=forms.Textarea, required=False)
    license = forms.CharField(required=False)
    license_description = forms.CharField(widget=forms.Textarea, required=False)
    
    commit_message = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        text = None
        info = kwargs.pop('info', None)
        
        super(DublinCoreForm, self).__init__(*args, **kwargs)
        
        if isinstance(info, dcparser.BookInfo):
            for name, value in info.to_dict().items():
                self.fields[name].initial = value
