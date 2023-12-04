from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PatientBaseRecord, PatientAnalysisCardiologist, PatientBloodTest, PatientBodyFatTest, PatientDermatologyTest, PatientDiagnosis, PatientThyroidTest, PatientTreatment
import uuid
from bootstrap_datepicker_plus.widgets import DatePickerInput

class RegisterForm(UserCreationForm):
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    

class RecordForm(forms.ModelForm):
    class Meta:
        model = PatientBaseRecord
        fields = ['first_name','last_name','age','date_of_birth','gender','contact_number',
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



from django.db import models

class DermatologyTestForm(forms.ModelForm):
    class Meta:
        model = PatientDermatologyTest
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

    def clean(self):
        cleaned_data = self.cleaned_data

        for field_name, field in self.fields.items():
            if isinstance(field, models.PositiveIntegerField):
                value = cleaned_data.get(field_name)
                if value is None or value == '':
                    # Set empty values to 0
                    cleaned_data[field_name] = 0

        cleaned_data = super().clean()

        return cleaned_data

class BodyFatTestForm(forms.ModelForm):
    class Meta:
        model = PatientBodyFatTest
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = PatientDiagnosis
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class TreatmentForm(forms.ModelForm):
    class Meta:
        model = PatientTreatment
        fields = "__all__"
        exclude = ['id', 'patient', 'doctor', 'date']

class ExaminationsForm(forms.ModelForm):
    class Meta:
        model = PatientDiagnosis
        fields = ['examinations']
