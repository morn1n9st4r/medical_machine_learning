from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from main.choices import CHESTPAIN_CHOICES, ECG_CHOICES, SLOPE_CHOICES
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientAnalysisCardiologist
import random


class Command(BaseCommand):
    help = 'Populates the PatientAnalysisCardiologist model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            record = PatientAnalysisCardiologist(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365)),
                type_of_pain=random.choice(CHESTPAIN_CHOICES)[0],
                bp=random.uniform(90, 180),  # Random blood pressure between 90 and 180
                restbp=random.uniform(60, 120),  # Random resting blood pressure between 60 and 120
                maxhr=random.uniform(50, 220),  # Random maximum heart rate between 50 and 220
                resting_ecg=random.choice(ECG_CHOICES)[0],
                excercise_angina=False,
                slope_st=random.choice(SLOPE_CHOICES)[0],
                st_depression=random.uniform(0, 5),  # Random ST depression between 0 and 5
                fluoroscopy_vessels=random.randint(0, 3),  # Random number of fluoroscopy vessels (0 to 3)
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientAnalysisCardiologist model.'))