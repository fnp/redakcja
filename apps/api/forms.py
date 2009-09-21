# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-20 21:34:52$"
__doc__ = "Micro-forms for the API."


from django import forms

class DocumentGetForm(forms.Form):
    autocabinet = forms.BooleanField(required=False)


class DocumentUploadForm(forms.Form):
    ocr = forms.FileField(label='Source OCR file')
    bookname = forms.RegexField(regex=r'[0-9\.\w_-]+',  \
        label='Publication name', help_text='Example: slowacki-beniowski')
    
    generate_dc = forms.BooleanField(required=False, initial=True, label=u"Generate DublinCore template")

