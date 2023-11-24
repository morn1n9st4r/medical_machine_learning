from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class PatientBaseRecord(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    date_of_birth = models.DateField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
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


class PatientAnalysisPhysician(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(PatientBaseRecord, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    type_of_pain = models.CharField(max_length=255)
    bp = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    restbp = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    maxhr = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    height = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()

    def __str__(self):
        return f"ID: {self.id} - Patient: {self.patient_id}, Doctor: {self.doctor_id}, Date: {self.date}"

    def get_model_type(self):
        return "PatientAnalysisPhysician"


class PatientBloodTest(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(PatientBaseRecord, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
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
    

class PatientDiagnosis(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(PatientBaseRecord, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    details = ...
    severity = ...
    details = ...
    details = ...
    #related_tests = ...
    

    def __str__(self):
        return f"Blood Test for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientBloodTest"