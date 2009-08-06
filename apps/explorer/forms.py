from django import forms


class BookForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    
