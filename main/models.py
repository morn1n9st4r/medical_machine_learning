import hashlib
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from .choices import *

from auditlog.registry import auditlog

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
    allergies = models.TextField(blank=True, default=0, null=True)
    chronic_diseases = models.TextField(blank=True, default=0, null=True)
    primary_doctor = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default=0, null=True)

    def __str__(self):
        return f"ID: {self.id} - {self.first_name} {self.last_name}, Age: {self.age}"


class DoctorBaseRecord(models.Model):
    id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15)
    specialties = models.TextField(blank=True, default=0, null=True)
    experience_years = models.IntegerField(blank=True, default=0, null=True)
    notes = models.TextField(blank=True, default=0, null=True)

    def __str__(self):
        return f"ID: {self.id} - Dr. {self.first_name} {self.last_name}, Age: {self.age}"


class MedicalRecordsABC(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    patient = models.ForeignKey(PatientBaseRecord, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorBaseRecord, on_delete=models.CASCADE)
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

class PatientThyroidTest(MedicalRecordsABC):
    
    ths = models.FloatField()
    t3 = models.FloatField()
    tt4 = models.FloatField()
    t4u = models.FloatField()
    fti = models.FloatField()
    tbg = models.FloatField()
    goitre = models.BooleanField()
    surgeries = models.BooleanField()

    def __str__(self):
        return f"Thyroid Hormones Test for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientThyroidTest"

class PatientDermatologyTest(MedicalRecordsABC):

    family_history = models.BooleanField()
    erythema = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    scaling = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    definite_borders = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    itching = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    koebner_phenomenon = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    polygonal_papules = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    follicular_papules = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    oral_mucosal_involvement = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    knee_and_elbow_involvement = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    scalp_involvement = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    melanin_incontinence = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    eosinophils_in_the_infiltrate = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    PNL_infiltrate = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    fibrosis_of_the_papillary_dermis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    exocytosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    acanthosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    hyperkeratosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    parakeratosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    clubbing_of_the_rete_ridges = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    elongation_of_the_rete_ridges = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    thinning_of_the_suprapapillary_epidermis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    spongiform_pustule = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    munro_microabcess = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    focal_hypergranulosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    disappearance_of_the_granular_layer = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    vacuolisation_and_damage_of_basal_layer = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    spongiosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    saw_tooth_appearance_of_retes = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    follicular_horn_plug = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    perifollicular_parakeratosis = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    inflammatory_monoluclear_inflitrate = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')
    band_like_infiltrate = models.CharField( choices=DERMATOLOGY_CHOICES, blank=True, default='0')

    def __str__(self):
        return f"Skin Test for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientDermatologyTest"


class PatientBodyFatTest(MedicalRecordsABC):
    height = models.FloatField()
    weight = models.FloatField()
    neck_circ = models.FloatField()
    chest_circ = models.FloatField()
    abdomen_circ = models.FloatField()
    hip_circ = models.FloatField()
    thigh_circ = models.FloatField()
    knee_circ = models.FloatField()
    ankle_cirk = models.FloatField()
    bicep_circ = models.FloatField()
    forearm_circ = models.FloatField()
    wrist_circ = models.FloatField()

    def __str__(self):
        return f"Body parts circumference Test for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientBodyFatTest"


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

    diagnosis = models.CharField()

    def __str__(self):
        return f"Diagnosis for {self.patient} on {self.date}"
    
    def get_model_type(self):
        return "PatientDiagnosis"

#class MLModel(models.Model):
#    pass

class ModelPrediction(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(PatientBaseRecord, on_delete=models.CASCADE)
    modelname = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)
    predicted_class = models.CharField(max_length=255)
    class_text = models.TextField()
    certainty = models.FloatField()

    def __str__(self):
        return f"Prediction #{self.id} - Model: {self.modelname}, Class: {self.predicted_class}, Certainty: {self.certainty}%"



auditlog.register(PatientBaseRecord, serialize_data=True)
auditlog.register(DoctorBaseRecord, serialize_data=True)
auditlog.register(PatientAnalysisPhysician, serialize_data=True)
auditlog.register(PatientBloodTest, serialize_data=True)
auditlog.register(PatientThyroidTest, serialize_data=True)
auditlog.register(PatientDermatologyTest, serialize_data=True)
auditlog.register(PatientBodyFatTest, serialize_data=True)
auditlog.register(PatientDiagnosis, serialize_data=True)
auditlog.register(PatientTreatment, serialize_data=True)
auditlog.register(ModelPrediction, serialize_data=True)