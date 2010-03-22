from django import forms
from wiki.models import Document, getstorage


class DocumentForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea)
    revision = forms.IntegerField(widget=forms.HiddenInput)
    comment = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        document = kwargs.pop('instance', None)
        super(DocumentForm, self).__init__(*args, **kwargs)
        if document:
            self.fields['name'].initial = document.name
            self.fields['text'].initial = document.text
            self.fields['revision'].initial = document.revision()
        
    def save(self, document_author = 'anonymous'):
        storage = getstorage()
        
        document = Document(storage, name=self.cleaned_data['name'], text=self.cleaned_data['text'])
        
        storage.put(document, 
                author = document_author, 
                comment = self.cleaned_data['comment'],
                parent =self.cleaned_data['revision'] )
        
        return storage.get(self.cleaned_data['name'])

