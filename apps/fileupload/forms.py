# -*- coding: utf-8 -*-
from django import forms


class UploadForm(forms.Form):
    files = forms.FileField()
