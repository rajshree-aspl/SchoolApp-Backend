# forms.py
from django import forms
from .models import User
from students.models import School

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'fullName', 'phone_number', 'dob', 'schoolid', 'password']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['schoolid'].queryset = School.objects.all()
