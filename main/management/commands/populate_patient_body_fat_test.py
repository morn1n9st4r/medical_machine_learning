import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientBodyFatTest

class Command(BaseCommand):
    help = 'Populates the PatientBodyFatTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()
            
            record = PatientBodyFatTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365)),
                height=random.uniform(1.5, 2.0),
                weight=random.uniform(50.0, 100.0),
                neck_circ=random.uniform(30.0, 50.0),
                chest_circ=random.uniform(70.0, 120.0),
                abdomen_circ=random.uniform(60.0, 110.0),
                hip_circ=random.uniform(80.0, 130.0),
                thigh_circ=random.uniform(40.0, 70.0),
                knee_circ=random.uniform(30.0, 50.0),
                ankle_cirk=random.uniform(20.0, 30.0),
                bicep_circ=random.uniform(20.0, 40.0),
                forearm_circ=random.uniform(20.0, 30.0),
                wrist_circ=random.uniform(15.0, 20.0),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientBodyFatTest model.'))