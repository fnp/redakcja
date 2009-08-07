from django import forms

from explorer import models


class BookForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    

class ImageFoldersForm(forms.Form):
    folders = forms.ChoiceField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ImageFoldersForm, self).__init__(*args, **kwargs)
        self.fields['folders'].choices = [('', '-- Wybierz folder z obrazkami --')] + [(fn, fn) for fn in models.get_image_folders()]

