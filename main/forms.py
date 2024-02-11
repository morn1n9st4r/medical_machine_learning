from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MedicalDrug, PatientBaseRecord, PatientAnalysisCardiologist, PatientBloodTest, PatientBodyFatTest, PatientDermatologyTest, PatientDiagnosis, PatientThyroidTest, PatientTreatment
import uuid
from bootstrap_datepicker_plus.widgets import DatePickerInput

class RegisterForm(UserCreationForm):
    
    email = forms.EmailField(required=True)
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the terms and conditions of usage and storage of my personal data.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    

class RecordForm(forms.ModelForm):
    class Meta:
        model = PatientBaseRecord
        fields = ['first_name','last_name','date_of_birth','gender','contact_number',
                'emergency_contact_number','emergency_contact_first_name', 'emergency_contact_last_name', 'emergency_contact_relationship',
                'allergies', 'chronic_diseases', 'primary_doctor', 'notes']
        widgets = {
            "date_of_birth": DatePickerInput()
        }


class CardiologistForm(forms.ModelForm):
    class Meta:
        model = PatientAnalysisCardiologist
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class BloodTestForm(forms.ModelForm):
    class Meta:
        model = PatientBloodTest
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class ThyroidTestForm(forms.ModelForm):
    class Meta:
        model = PatientThyroidTest
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class DermatologyTestForm(forms.ModelForm):
    class Meta:
        model = PatientDermatologyTest
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class BodyFatTestForm(forms.ModelForm):
    class Meta:
        model = PatientBodyFatTest
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = PatientDiagnosis
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date', 'examinations']

class TreatmentForm(forms.ModelForm):
    medicine = forms.ModelChoiceField(
        queryset=MedicalDrug.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PatientTreatment
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class ExaminationsForm(forms.ModelForm):
    class Meta:
        model = PatientDiagnosis
        fields = ['examinations']
