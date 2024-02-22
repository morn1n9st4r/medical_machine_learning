import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientBloodTest
import numpy as np

from main.utils import create_diagnosis, create_treatment

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

            if record.gct > 2.7 and record.bil > 2.7:
                diag_id = create_diagnosis(patient, 'Cirrhosis', 'MO', 'inflammation of liver', 'HD', False, record)
                create_treatment(patient, 'Spironolactone', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Furosemide', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Lactulose', 1, 'tablet', 'DA', diag_id)
            elif record.chol > 183 and record.crea > 1.2:
                diag_id = create_diagnosis(patient, 'Chronic Kidney Failure', 'SE', 'decrease in kidney function', 'HD', False, record)
                create_treatment(patient, 'Erythropoietin', 1, 'injection', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Iron supplement', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Calcitriol', 1, 'tablet', 'DA', diag_id)
            elif record.alp > 100 and record.ast > 35:
                diag_id = create_diagnosis(patient, 'Mononucleosis', 'MO', 'the Epstein-Barr virus', 'HD', False, record)
                create_treatment(patient, 'Acetaminophen', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Ibuprofen', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Corticosteroids', 1, 'tablet', 'DA', diag_id)
            elif record.alb > 4.5 and record.bg < 90:
                diag_id = create_diagnosis(patient, 'Dehydration with Hypoglycemia', 'MO', 'loss of fluids with low blood sugar levels', 'HD', False, record)
                create_treatment(patient, 'Oral rehydration salts', 1, 'sachet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Glucose tablets', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Intravenous fluids', 1, 'bag', 'DA', diag_id)
            elif record.alp > 110 and record.alt < 30 and record.ast > 40:
                diag_id = create_diagnosis(patient, 'Possible Hepatitis with Mild ALT Elevation', 'MO', 'inflammation of the liver with mild increase in ALT', 'HD', False, record)
                create_treatment(patient, 'Antiviral medication', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Liver protective medication', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Vitamin B complex', 1, 'tablet', 'DA', diag_id)
            elif record.bil > 1.2 and record.gct > 1.0 and record.prot < 6.7:
                diag_id = create_diagnosis(patient, 'Advanced Liver Disease with Hypoproteinemia', 'MO', 'severe damage to the liver with low protein levels', 'HD', False, record)
                create_treatment(patient, 'Albumin', 1, 'injection', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Vitamin K', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Protein supplement', 1, 'sachet', 'DA', diag_id)
            elif record.chol > 183 and record.crea > 1.2 and record.che < 8:
                diag_id = create_diagnosis(patient, 'Chronic Kidney Failure with Low Cholinesterase', 'SE', 'decrease in kidney function with low cholinesterase levels', 'HD', False, record)
                create_treatment(patient, 'Erythropoietin', 1, 'injection', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Ferrous sulfate', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Calcitriol', 1, 'tablet', 'DA', diag_id)
            elif record.alb > 4.5 and record.bg > 95:
                diag_id = create_diagnosis(patient, 'Diabetes with Dehydration', 'MO', 'high blood sugar levels with loss of fluids', 'HD', False, record)
                create_treatment(patient, 'Insulin', 1, 'injection', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Oral rehydration salts', 1, 'sachet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Metformin', 1, 'tablet', 'DA', diag_id)
            elif record.alp > 150 and record.alt > 45 and record.ast > 40:
                diag_id = create_diagnosis(patient, 'Hepatitis with Liver Damage', 'MO', 'inflammation of the liver with damage to liver cells', 'HD', False, record)
                create_treatment(patient, 'Entecavir', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Silymarin', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Vitamin B complex', 1, 'tablet', 'DA', diag_id)
            elif record.bil > 1.2 and record.gct > 2.7 and record.prot > 7.85:
                diag_id = create_diagnosis(patient, 'Advanced Liver Disease', 'MO', 'severe damage to the liver', 'HD', False, record)
                create_treatment(patient, 'Albumin', 1, 'injection', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Vitamin K', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Protein supplement', 1, 'sachet', 'DA', diag_id)
            elif record.chol > 183 and record.crea > 1.2 and record.che > 10:
                diag_id = create_diagnosis(patient, 'Chronic Kidney Failure with Organ Damage', 'SE', 'decrease in kidney function with damage to organs', 'HD', False, record)
                create_treatment(patient, 'Erythropoietin', 1, 'injection', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Ferrous sulfate', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Calcitriol', 1, 'tablet', 'DA', diag_id)



        self.stdout.write(self.style.SUCCESS('Successfully populated PatientBloodTest model.'))