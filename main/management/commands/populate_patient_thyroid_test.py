import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry
from main.models import PatientBaseRecord, PatientThyroidTest
import numpy as np

class Command(BaseCommand):
    help = 'Populates the PatientThyroidTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            # Define mean and standard deviation for each attribute
            tsh_mean, tsh_std = 2.2, 0.9
            t3_mean, t3_std = 150, 25
            tt4_mean, tt4_std = 8, 1.5
            t4u_mean, t4u_std = 1.3, 0.25
            fti_mean, fti_std = 1.3, 0.3

            record = PatientThyroidTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365*3)),
                tsh=np.random.normal(tsh_mean, tsh_std),
                t3=np.random.normal(t3_mean, t3_std),
                tt4=np.random.normal(tt4_mean, tt4_std),
                t4u=np.random.normal(t4u_mean, t4u_std),
                fti=np.random.normal(fti_mean, fti_std),
                goitre=random.choice([True, False]),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientThyroidTest model.'))