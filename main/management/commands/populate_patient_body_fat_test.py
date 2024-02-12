import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientBodyFatTest
import numpy as np

class Command(BaseCommand):
    help = 'Populates the PatientBodyFatTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            # Define mean and standard deviation for each attribute
            height_mean, height_std = 1.75, 0.1
            weight_mean, weight_std = 75, 15
            neck_circ_mean, neck_circ_std = 40, 5
            chest_circ_mean, chest_circ_std = 95, 15
            abdomen_circ_mean, abdomen_circ_std = 85, 10
            hip_circ_mean, hip_circ_std = 105, 15
            thigh_circ_mean, thigh_circ_std = 55, 7
            knee_circ_mean, knee_circ_std = 40, 5
            ankle_cirk_mean, ankle_cirk_std = 25, 3
            bicep_circ_mean, bicep_circ_std = 30, 5
            forearm_circ_mean, forearm_circ_std = 25, 3
            wrist_circ_mean, wrist_circ_std = 17.5, 1.5

            record = PatientBodyFatTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365*3)),
                height=np.random.normal(height_mean, height_std),
                weight=np.random.normal(weight_mean, weight_std),
                neck_circ=np.random.normal(neck_circ_mean, neck_circ_std),
                chest_circ=np.random.normal(chest_circ_mean, chest_circ_std),
                abdomen_circ=np.random.normal(abdomen_circ_mean, abdomen_circ_std),
                hip_circ=np.random.normal(hip_circ_mean, hip_circ_std),
                thigh_circ=np.random.normal(thigh_circ_mean, thigh_circ_std),
                knee_circ=np.random.normal(knee_circ_mean, knee_circ_std),
                ankle_cirk=np.random.normal(ankle_cirk_mean, ankle_cirk_std),
                bicep_circ=np.random.normal(bicep_circ_mean, bicep_circ_std),
                forearm_circ=np.random.normal(forearm_circ_mean, forearm_circ_std),
                wrist_circ=np.random.normal(wrist_circ_mean, wrist_circ_std),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientBodyFatTest model.'))