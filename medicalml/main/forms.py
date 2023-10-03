from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Record


class RegisterForm(UserCreationForm):
    
    # id instead of username
    
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['patient_name', 'age', 'sex', 'chest_pain_type', 'resting_bp',
                    'cholesterol', 'fasting_blood_sugar','resting_ecg', 'max_heart_rate',
                    'exercise_angina', 'oldpeak', 'st_slope']
