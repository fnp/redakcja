from django import forms

class UploadForm(forms.Form):
    files = forms.FileField()
