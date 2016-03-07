from django import forms
from .models import Organization, UserCard, countries

class OrganizationForm(forms.ModelForm):
    cts = countries

    class Meta:
        model = Organization
        exclude = ['_html']

class UserCardForm(forms.ModelForm):
    cts = countries

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = UserCard
        exclude = ['_html', 'user']

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs['initial'] = {
                'first_name': kwargs['instance'].user.first_name,
                'last_name': kwargs['instance'].user.last_name,
            }
        return super(UserCardForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.user.first_name = self.cleaned_data.get('first_name', '')
        self.instance.user.last_name = self.cleaned_data.get('last_name', '')
        self.instance.user.save()
        return super(UserCardForm, self).save(*args, **kwargs)

