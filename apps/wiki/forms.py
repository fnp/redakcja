# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.  
#
from django import forms
from wiki.models import Document, getstorage
from django.utils.translation import ugettext_lazy as _ 


class DocumentForm(forms.Form):
    """ Old form for saving document's text """
    
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
    
class DocumentTagForm(forms.Form):
    TAGS = (
        ("publish", "Do publikacji"),        
    )
        
    tag = forms.ChoiceField(choices = TAGS)
    version = forms.IntegerField(widget = forms.HiddenInput)

class DocumentTextSaveForm(forms.Form):
    """ 
    Form for saving document's text:
           
        * name - document's storage identifier.
        * parent_revision - revision which the modified text originated from.
        * comment - user's verbose comment; will be used in commit.
        * stage_completed - mark this change as end of given stage.
               
    """
    DOC_STAGES = (
        ('', 'Nic konkretnego'),
        ('tagging', 'Tagowanie'),
        ('modernized', 'Uwspółcześnienia'),
        ('editing', 'Redakcja'),
    )    
                
    id = forms.CharField(widget=forms.HiddenInput)
    parent_revision = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.HiddenInput)
    
    author = forms.CharField(
        required = False,
        label = _(u"Autor"),
        help_text = _(u"Twoje imie i nazwisko lub email.")
    )
    
    comment = forms.CharField(
        required = True, 
        widget=forms.Textarea,
        label = _(u"Twój komentarz"),
        help_text = _(u"Opisz w miarę dokładnie swoje zmiany."), 
    )
    
    stage_completed = forms.ChoiceField(
        choices=DOC_STAGES, 
        required= False,        
        label = _(u"Skończyłem robić"),
        help_text = _(u"Jeśli skończyłeś jeden z etapów utworu, wybierz go."),
    )
    