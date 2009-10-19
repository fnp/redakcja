# -*- encoding: utf-8 -*-

__author__= "Łukasz Rekucki"
__date__ = "$2009-09-20 21:34:52$"
__doc__ = "Micro-forms for the API."

from django import forms
from api.models import PullRequest
from django.contrib.auth.models import User

import re
from django.utils import simplejson as json


class MergeRequestForm(forms.Form):
    # should the target document revision be updated or shared
    type = forms.ChoiceField(choices=(('update', 'Update'), ('share', 'Share')) )
    
    #
    # if type == update:
    #   * user's revision which is the base of the merge
    # if type == share:
    #   * revision which will be pulled to the main branch
    #
    # NOTE: the revision doesn't have to be owned by the user
    #  who requests the merge:
    #   a) Every user can update his branch
    #   b) Some users can push their changes
    #     -> if they can't, they leave a PRQ
    #   c) Some users can pull other people's changes
    #   d) Some users can update branches owned by special
    #    users associated with PRQ's
    revision = forms.RegexField('[0-9a-f]{40}')

    # any additional comments that user wants to add to the change
    message = forms.CharField(required=False)

class DocumentUploadForm(forms.Form):
    ocr_file = forms.FileField(label='Source OCR file', required=False)
    ocr_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    bookname = forms.RegexField(regex=r'[0-9\.\w_-]+',  \
        label='Publication name', help_text='Example: słowacki__beniowski__pieśń_1')
    
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

PRQ_USER_RE = re.compile(r"^\$prq-(\d{1,10})$", re.UNICODE)

class DocumentRetrieveForm(forms.Form):    
    revision = forms.RegexField(regex=r'latest|[0-9a-z]{40}', required=False)
    user = forms.CharField(required=False)

    def clean_user(self):
        # why, oh why does django doesn't implement this!!!
        # value = super(DocumentRetrieveForm, self).clean_user()
        value = self.cleaned_data['user']        
        
        if value.startswith('$'):
            # library user (... maybe later)
            if value == '$library':
                raise forms.ValidationError("Invalid user name '%s'" % value)

            m = PRQ_USER_RE.match(value)
            
            if m:
                try:
                    return value
                except:
                    raise forms.ValidationError("User doesn't exist.")
            raise forms.ValidationError("Invalid user name '%s'" % value)
        try:
            return value
        except:
            raise forms.ValidationError("User doesn't exist.")                
           

class TextRetrieveForm(DocumentRetrieveForm):
    part = forms.CharField(required=False)

class TextUpdateForm(DocumentRetrieveForm):
    message = forms.CharField(required=False)
    contents = forms.CharField(required=False)
    chunks = forms.CharField(required=False)

    def clean_message(self):
        value = self.cleaned_data['message']

        if value:
            return u"$USER$ " + value
        else:
            return u"$AUTO$ XML content update."

    def clean_chunks(self):
        value = self.cleaned_data['chunks']

        try:
            return json.loads(value)
        except Exception, e:
            forms.ValidationError("Invalid JSON: " + e.message)


    def clean(self):
        if self.cleaned_data['contents'] and self.cleaned_data['chunks']:
            raise forms.ValidationError("Pass either contents or chunks - not both ")

        if not self.cleaned_data['contents'] and not self.cleaned_data['chunks']:
            raise forms.ValidationError("You must pass contents or chunks.")

        return self.cleaned_data