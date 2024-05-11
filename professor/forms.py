from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  


class registrationform(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username','password1','password2','first_name','last_name','email','middle_name','contact_number']


class edit_profile_form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','middle_name']

class additional_data_form(forms.ModelForm):
    class Meta:
        model = additional_data
        exclude = ['user']


class classesform(forms.ModelForm):
    class Meta:
        model = classes
        exclude = ['user','disabled']
        
class standardform(forms.ModelForm):
    class Meta:
        model = standard
        exclude = ['user','disabled']

class subjectform(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['standard'].queryset = standard.objects.filter(user=user).filter(disabled=False)
            self.fields['classes'].queryset = classes.objects.filter(user=user).filter(disabled=False)
    
    
    class Meta:
        model = subject
        exclude = ['user','disabled']




class daily_schedule_form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['subject'].queryset = subject.objects.filter(user=user).filter(disabled=False)
            
    class Meta:
        model = daily_schedule
        exclude = ['user','amount']



