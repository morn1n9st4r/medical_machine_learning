from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PatientBaseRecord, PatientAnalysisPhysician, PatientBloodTest, PatientDiagnosis, PatientTreatment
import uuid

class RegisterForm(UserCreationForm):
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    

class RecordForm(forms.ModelForm):
    class Meta:
        model = PatientBaseRecord
        fields = ['first_name','last_name','age','date_of_birth','gender','contact_number']


class PhysicianForm(forms.ModelForm):
    class Meta:
        model = PatientAnalysisPhysician
        fields = ['type_of_pain','bp','restbp','maxhr','height','weight']


class BloodTestForm(forms.ModelForm):
    class Meta:
        model = PatientBloodTest
        fields = ['alb', 'alp', 'alt', 'ast', 'bil', 'bg', 'che', 'chol', 'crea', 'gct', 'prot']


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = PatientDiagnosis
        fields = ['disease_name', 'severity', 'tags', 'details']

class TreatmentForm(forms.ModelForm):
    class Meta:
        model = PatientTreatment
        fields = ['medicine', 'quantity', 'quantity_type', 'frequency', 'start_date', 'finish_date', 'form', 'diagnosis']

class ExaminationsForm(forms.ModelForm):
    class Meta:
        model = PatientDiagnosis
        fields = ['examinations']
