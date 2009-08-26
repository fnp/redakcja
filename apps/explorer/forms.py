from django import forms

from lxml import etree
from librarian import dcparser

from explorer import models

class BookForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
    message = forms.CharField(required=False)

class ImageFoldersForm(forms.Form):
    folders = forms.ChoiceField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ImageFoldersForm, self).__init__(*args, **kwargs)
        self.fields['folders'].choices = [('', '-- Wybierz folder z obrazkami --')] + [(fn, fn) for fn in models.get_image_folders()]


class DublinCoreForm(forms.Form):
    wiki_url = forms.URLField(verify_exists=False)
    author = forms.CharField()
    title = forms.CharField()
    epoch = forms.CharField()
    kind = forms.CharField()
    genre = forms.CharField()
    created_at = forms.DateField()
    released_to_public_domain_at = forms.DateField()
    translator = forms.CharField(required=False)
    technical_editor = forms.CharField(required=False)
    publisher = forms.CharField()
    source_name = forms.CharField(widget=forms.Textarea)
    source_url = forms.URLField(verify_exists=False)
    url = forms.URLField(verify_exists=False)
    parts = forms.CharField(widget=forms.Textarea, required=False)
    license = forms.CharField(required=False)
    license_description = forms.CharField(widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        text = None
        if 'text' in kwargs:
            text = kwargs.pop('text')
        
        super(DublinCoreForm, self).__init__(*args, **kwargs)
        
        if text is not None:
            book_info = dcparser.BookInfo.from_string(text)
            for name, value in book_info.to_dict().items():
                self.fields[name].initial = value
    
    def save(self, repository, path):
        file_contents = repository.get_file(path).data()
        doc = etree.fromstring(file_contents)
                
        book_info = dcparser.BookInfo()
        for name, value in self.cleaned_data.items():
            if value is not None and value != '':
                setattr(book_info, name, value)
        rdf = etree.XML(book_info.to_xml())
        
        old_rdf = doc.getroottree().find('//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
        old_rdf.getparent().remove(old_rdf)
        doc.insert(0, rdf)
        repository.add_file(path, unicode(etree.tostring(doc), 'utf-8'))

