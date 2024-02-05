from django.core.management.base import BaseCommand
from datetime import datetime
from main.models import PatientBaseRecord, PatientAnalysisCardiologist

class Command(BaseCommand):
    help = 'Populates the PatientAnalysisCardiologist model with 40 instances.'

    def handle(self, *args, **options):
        patient = PatientBaseRecord.objects.first()  

        for i in range(40):
            record = PatientAnalysisCardiologist(
                patient=patient,
                date=datetime.now(),
                type_of_pain='Type1',
                bp=120,
                restbp=80,
                maxhr=60,
                resting_ecg='Normal',
                excercise_angina=False,
                slope_st='Flat',
                st_depression=0.0,
                fluoroscopy_vessels=0,
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientAnalysisCardiologist model.'))