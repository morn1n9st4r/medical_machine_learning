from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PatientBaseRecord, PatientAnalysisPhysician


class RegisterForm(UserCreationForm):
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
class RecordForm(forms.ModelForm):
    class Meta:
        model = PatientBaseRecord
        fields = ['first_name','last_name','age','date_of_birth','gender','contact_number']



class BloodTestForm(forms.ModelForm):
    pass

class PhysicianForm(forms.ModelForm):
    class Meta:
        model = PatientAnalysisPhysician
        fields = ['type_of_pain','bp','restbp','maxhr','height','weight','date']