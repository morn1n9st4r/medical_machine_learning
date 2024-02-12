import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientBloodTest
import numpy as np

class Command(BaseCommand):
    help = 'Populates the PatientBloodTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            # Define mean and standard deviation for each attribute
            alb_mean, alb_std = 4.5, 0.5
            alp_mean, alp_std = 80, 30
            alt_mean, alt_std = 32, 15
            ast_mean, ast_std = 25, 10
            bil_mean, bil_std = 0.65, 0.3
            bg_mean, bg_std = 85, 10
            che_mean, che_std = 8, 2
            chol_mean, chol_std = 162.5, 20
            crea_mean, crea_std = 1, 0.2
            gct_mean, gct_std = 2.5, 0.25
            prot_mean, prot_std = 7.25, 0.625

            record = PatientBloodTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365*3)),
                alb=np.random.normal(alb_mean, alb_std),
                alp=int(np.random.normal(alp_mean, alp_std)),
                alt=int(np.random.normal(alt_mean, alt_std)),
                ast=int(np.random.normal(ast_mean, ast_std)),
                bil=np.random.normal(bil_mean, bil_std),
                bg=np.random.normal(bg_mean, bg_std),
                che=np.random.normal(che_mean, che_std),
                chol=int(np.random.normal(chol_mean, chol_std)),
                crea=np.random.normal(crea_mean, crea_std),
                gct=np.random.normal(gct_mean, gct_std),
                prot=np.random.normal(prot_mean, prot_std),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientBloodTest model.'))