import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry
from main.models import PatientBaseRecord, PatientThyroidTest
import numpy as np

from main.utils import create_diagnosis, create_treatment

class Command(BaseCommand):
    help = 'Populates the PatientThyroidTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(20):
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

            if record.tsh > 2.81  and record.t3 < 134 and record.t4u > 1.37 and record.fti < 1.08:
                diag_id = create_diagnosis(patient, 'Hypothyroidism with Thyroid Hormone Resistance', 'MO', 'underactive thyroid gland with resistance to thyroid hormones', 'EN', False, record)
                create_treatment(patient, 'Levothyroxine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Liothyronine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Triiodothyronine', 1, 'tablet', 'DA', diag_id)
            elif record.tsh < 1.41 and record.t3 > 164 and record.tt4 > 8.79:
                diag_id = create_diagnosis(patient, 'Hyperthyroidism with High TT4', 'MO', 'overactive thyroid gland with high total T4', 'EN', False, record)
                create_treatment(patient, 'Methimazole', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Propranolol', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Propylthiouracil', 1, 'tablet', 'DA', diag_id)
            elif record.tt4 > 8.7 and record.t4u > 1.37 and record.fti < 1.1:
                diag_id = create_diagnosis(patient, 'Thyroid Hormone Resistance', 'MO', 'resistance to thyroid hormones', 'EN', False, record)
                create_treatment(patient, 'Levothyroxine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Triiodothyronine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Beta blockers', 1, 'tablet', 'DA', diag_id)
            elif record.tsh > 2.97 and record.t3 < 129:
                diag_id = create_diagnosis(patient, 'Hypothyroidism', 'MO', 'underactive thyroid gland', 'EN', False, record)
                create_treatment(patient, 'Levothyroxine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Liothyronine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Thyroid supplement', 1, 'tablet', 'DA', diag_id)
            elif record.tsh < 1.48 and record.t3 > 169:
                diag_id = create_diagnosis(patient, 'Hyperthyroidism', 'MO', 'overactive thyroid gland', 'EN', False, record)
                create_treatment(patient, 'Methimazole', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Propranolol', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Radioactive iodine', 1, 'dose', 'DA', diag_id)  
            elif record.tsh > 2.86 and record.t3 < 133:
                diag_id = create_diagnosis(patient, 'Hypothyroidism', 'MO', 'underactive thyroid gland with enlarged thyroid gland', 'EN', False, record)
                create_treatment(patient, 'Levothyroxine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Potassium iodide', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Liothyronine', 1, 'tablet', 'DA', diag_id)
            elif record.t4u > 1.37 and record.fti < 1.07 and record.goitre:
                diag_id = create_diagnosis(patient, 'Thyroid Hormone Resistance with Goitre', 'MO', 'resistance to thyroid hormones with enlarged thyroid gland', 'EN', False, record)
                create_treatment(patient, 'Levothyroxine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Triiodothyronine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Potassium iodide', 1, 'tablet', 'DA', diag_id)






        self.stdout.write(self.style.SUCCESS('Successfully populated PatientThyroidTest model.'))