import hashlib
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from .choices import *

class PatientBaseRecord(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15)
    emergency_contact_number = models.CharField(max_length=15)
    emergency_contact_first_name = models.CharField(max_length=255)
    emergency_contact_last_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=255)
    allergies = models.TextField(blank=True, null=True)
    chronic_diseases = models.TextField(blank=True, null=True)
    primary_doctor = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ID: {self.id} - {self.first_name} {self.last_name}, Age: {self.age}, Gender: {self.get_gender_display()}, Primary Doctor: {self.primary_doctor}"



class MedicalRecordsABC(models.Model):
    #id = models.AutoField()
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    patient = models.ForeignKey(PatientBaseRecord, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    
    class Meta:
        abstract = True

    @property
    def shortened_id(self):
        uuid_bytes = self.id.bytes
        md5_digest = hashlib.md5(uuid_bytes).digest()
        shortened_value = md5_digest[:8]
        shortened_hex = shortened_value.hex()
        return shortened_hex


class PatientAnalysisPhysician(MedicalRecordsABC):

    type_of_pain = models.CharField(max_length=255)
    bp = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    restbp = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    maxhr = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    height = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"ID: {self.id} - Patient: {self.patient_id}, Doctor: {self.doctor_id}, Date: {self.date}"

    def get_model_type(self):
        return "PatientAnalysisPhysician"


class PatientBloodTest(MedicalRecordsABC):

    alb = models.FloatField()
    alp = models.FloatField()
    alt = models.FloatField()
    ast = models.FloatField()
    bil = models.FloatField()
    bg = models.FloatField()
    che = models.FloatField()
    chol = models.FloatField()
    crea = models.FloatField()
    gct = models.FloatField()
    prot = models.FloatField()

    def __str__(self):
        return f"Blood Test for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientBloodTest"

class PatientDiagnosis(MedicalRecordsABC):

    disease_name = models.CharField()
    severity = models.CharField(max_length=2, choices=SEVERITY_CHOICES)   
    details = models.CharField()
    tags = models.CharField(max_length=2, choices=TAGS_CHOICES)

    examinations = models.CharField()

    def __str__(self):
        return f"Diagnosis for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientDiagnosis"

    
class PatientTreatment(MedicalRecordsABC):

    medicine = models.CharField()
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    quantity_type = models.CharField()
    frequency = models.CharField( choices=FREQUENCY_CHOICES) 
    start_date = models.DateField()
    finish_date = models.DateField()
    form = models.CharField(choices=FORM_CHOICES)

    diagnosis = models.ForeignKey(PatientDiagnosis, on_delete=models.CASCADE)

    def __str__(self):
        return f"Diagnosis for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientDiagnosis"