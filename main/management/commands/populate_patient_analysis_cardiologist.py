from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from main.choices import CHESTPAIN_CHOICES, ECG_CHOICES, SLOPE_CHOICES
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientAnalysisCardiologist
import random
import numpy as np

class Command(BaseCommand):
    help = 'Populates the PatientAnalysisCardiologist model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            # Define mean and standard deviation for each attribute
            bp_mean, bp_std = 135, 20
            restbp_mean, restbp_std = 90, 15
            maxhr_mean, maxhr_std = 150, 30
            st_depression_mean, st_depression_std = 2.5, 1

            record = PatientAnalysisCardiologist(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365*3)),
                type_of_pain=random.choice(CHESTPAIN_CHOICES)[0],
                bp=np.random.normal(bp_mean, bp_std),  # Blood pressure from normal distribution
                restbp=np.random.normal(restbp_mean, restbp_std),  # Resting blood pressure from normal distribution
                maxhr=np.random.normal(maxhr_mean, maxhr_std),  # Maximum heart rate from normal distribution
                resting_ecg=random.choice(ECG_CHOICES)[0],
                excercise_angina=False,
                slope_st=random.choice(SLOPE_CHOICES)[0],
                st_depression=np.random.normal(st_depression_mean, st_depression_std),  # ST depression from normal distribution
                fluoroscopy_vessels=random.randint(0, 3),  # Random number of fluoroscopy vessels (0 to 3)
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientAnalysisCardiologist model.'))