import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientBloodTest

class Command(BaseCommand):
    help = 'Populates the PatientBloodTest model with 1 instances.'

    def handle(self, *args, **options):
        patient = PatientBaseRecord.objects.order_by('?').first()

        for i in range(1):
            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            record = PatientBloodTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365)),
                alb=random.uniform(3.5, 5.5),
                alp=random.randint(20, 140),
                alt=random.randint(7, 56),
                ast=random.randint(10, 40),
                bil=random.uniform(0.1, 1.2),
                bg=random.uniform(70, 100),
                che=random.uniform(4.6, 11.2),
                chol=random.randint(125, 200),
                crea=random.uniform(0.7, 1.3),
                gct=random.uniform(2.0, 3.0),
                prot=random.uniform(6.0, 8.5),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientBloodTest model.'))