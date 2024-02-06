import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry
from main.models import PatientBaseRecord, PatientThyroidTest

class Command(BaseCommand):
    help = 'Populates the PatientThyroidTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()
            
            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()
            
            record = PatientThyroidTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365)),
                tsh=random.uniform(0.4, 4.0),
                t3=random.uniform(100, 200),
                tt4=random.uniform(5.0, 11.0),
                t4u=random.uniform(0.8, 1.8),
                fti=random.uniform(0.7, 1.9),
                goitre=random.choice([True, False]),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientThyroidTest model.'))