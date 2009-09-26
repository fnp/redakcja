# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-20 21:34:52$"
__doc__ = "Micro-forms for the API."


from django import forms

class DocumentEntryRequest(forms.Form):
    revision = forms.RegexField(regex='latest|[0-9a-f]{40}')

class DocumentUploadForm(forms.Form):
    ocr_file = forms.FileField(label='Source OCR file', required=False)
    ocr_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    bookname = forms.RegexField(regex=r'[0-9\.\w_-]+',  \
        label='Publication name', help_text='Example: slowacki-beniowski')
    
    generate_dc = forms.BooleanField(required=False, \
        initial=True, label=u"Generate DublinCore template")


    def clean(self):
        clean_data = self.cleaned_data

        ocr_file = clean_data['ocr_file']
        ocr_data = clean_data['ocr_data']

        if not ocr_file and not ocr_data:
            raise forms.ValidationError(
                "You must either provide file descriptor or raw data." )

        return clean_data