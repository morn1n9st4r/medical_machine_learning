from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Record(models.Model):

    class SexChoises(models.TextChoices):
        M = 'M', ('Male')
        F = 'F', ('Female')
        
    class ChestPainChoises(models.TextChoices):
        TA = 'TA', ('Typical_Angina')
        ATA = 'ATA', ('Atypical_Angina')
        NAP = 'NAP', ('Non_Anginal_Pain')
        ASY = 'ASY', ('Asymptomatic')
        
    class FastingBSChoises(models.TextChoices):
        N = 'N', ('Nornal')
        H = 'H', ('High')

    class ECGChoises(models.TextChoices):
        Normal = 'Normal', ('Nornal')
        ST = 'ST', ('st-t_wave_abnormality')
        LVH = 'LVH', ('left_ventricular_hypertrophy')

    class AnginaChoises(models.TextChoices):
        Y = 'Y', ('Yes')
        N = 'N', ('No')

    class STChoises(models.TextChoices):
        Up = 'Up', ('upsloping')
        Flat = 'Flat', ('flat')
        Down = 'Down', ('downsloping')

    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    patient_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=SexChoises.choices)
    chest_pain_type = models.CharField(max_length=3, choices=ChestPainChoises.choices)
    resting_bp = models.IntegerField()
    cholesterol = models.IntegerField()
    fasting_blood_sugar = models.CharField(max_length=1, choices=FastingBSChoises.choices)
    resting_ecg = models.CharField(max_length=6, choices=ECGChoises.choices)
    max_heart_rate = models.IntegerField()
    exercise_angina = models.CharField(max_length=1, choices=AnginaChoises.choices)
    oldpeak = models.IntegerField()
    st_slope = models.CharField(max_length=4, choices=STChoises.choices)

    def __str__(self) -> str:
        return self.patient_name + "\n" + \
               self.age + "\n" + \
               self.sex + "\n" + \
               self.chest_pain_type + "\n" + \
               self.resting_bp + "\n" + \
               self.cholesterol + "\n" + \
               self.fasting_blood_sugar + "\n" + \
               self.resting_ecg + "\n" + \
               self.max_heart_rate + "\n" + \
               self.exercise_angina + "\n" + \
               self.oldpeak + "\n" + \
               self.st_slope