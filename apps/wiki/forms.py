from django import forms
from wiki.models import Document, storage


class DocumentForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea)
    revision = forms.IntegerField(widget=forms.HiddenInput)
    author = forms.CharField()
    comment = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        document = kwargs.pop('instance', None)
        super(DocumentForm, self).__init__(*args, **kwargs)
        if document:
            self.fields['name'].initial = document.name
            self.fields['text'].initial = document.text
            self.fields['revision'].initial = document.revision()
    
    def get_storage(self):
        return storage
    
    def save(self):
        document = Document(self.get_storage(), name=self.cleaned_data['name'], text=self.cleaned_data['text'])
        storage.put(document, self.cleaned_data['author'], self.cleaned_data['comment'],
            self.cleaned_data['revision'])
        return storage.get(self.cleaned_data['name'])

