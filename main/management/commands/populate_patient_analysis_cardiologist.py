from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from main.choices import CHESTPAIN_CHOICES, ECG_CHOICES, SLOPE_CHOICES
from main.models import DoctorBaseRecord, MedicalRecordRegistry, PatientBaseRecord, PatientAnalysisCardiologist, PatientDiagnosis, PatientTreatment
import random
import numpy as np


class Command(BaseCommand):
    help = 'Populates the PatientAnalysisCardiologist model with 1 instances.'

    def handle(self, *args, **options):

        def create_diagnosis(patient, diag, severity, details, tags, cured, examination):
            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            medical_diagnosis = PatientDiagnosis(
                id=latest_record.id,
                doctor = DoctorBaseRecord.objects.order_by('?').first(),
                patient=patient,
                date=examination.date + timedelta(days=random.randint(0, 365)),
                disease_name=diag,
                severity=severity,
                details=details,
                tags=tags,
                cured=cured,
                examinations=str(examination.id)
                )
            medical_diagnosis.save()
            return latest_record.id

        def create_treatment(patient, medicine, quantity, quantity_type, frequency, diagnosis_id):

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            target_diag = PatientDiagnosis.objects.filter(id=diagnosis_id).first()

            medical_treatment = PatientTreatment(
                id=latest_record.id,
                doctor = DoctorBaseRecord.objects.order_by('?').first(),
                patient=patient,
                date=target_diag.date  + timedelta(days=random.randint(0, 14)),
                medicine=medicine,
                quantity=quantity,
                quantity_type=quantity_type,
                frequency=frequency,
                start_date=target_diag.date  + timedelta(days=random.randint(14, 28)),
                finish_date=target_diag.date  + timedelta(days=random.randint(28, 140)),
                diagnosis=diagnosis_id
                )
            medical_treatment.save()
            return latest_record


        for i in range(20):
            patient = PatientBaseRecord.objects.order_by('?').first()

            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()

            # Define mean and standard deviation for each attribute
            bp_mean, bp_std = 135, 20
            restbp_mean, restbp_std = 90, 15
            maxhr_mean, maxhr_std = 150, 30
            st_depression_mean, st_depression_std = 1.5, 0.9

            possible_values = [0, 1, 2, 3]
            weights = [8, 1, 1, 1] 

            record = PatientAnalysisCardiologist(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365*3)),
                type_of_pain=random.choice(CHESTPAIN_CHOICES)[0],
                bp=np.random.normal(bp_mean, bp_std),  # Blood pressure from normal distribution
                restbp=np.random.normal(restbp_mean, restbp_std),  # Resting blood pressure from normal distribution
                maxhr=np.random.normal(maxhr_mean, maxhr_std),  # Maximum heart rate from normal distribution
                resting_ecg=random.choice(ECG_CHOICES)[0],
                excercise_angina=False,
                slope_st=random.choice(SLOPE_CHOICES)[0],
                st_depression=np.random.normal(st_depression_mean, st_depression_std),  # ST depression from normal distribution
                fluoroscopy_vessels=random.choices(possible_values, weights)[0],  # Random number of fluoroscopy vessels (0 to 3)
            )
            record.save()


            if record.bp >= 158:
                sev = 'MI' if record.bp < 162 else 'MO'
                diag_id = create_diagnosis(patient, 'Hypertension', sev, 'high blood pressure', 'CV', False, record)
                create_treatment(patient, 'Lisinopril', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Amlodipine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Hydrochlorothiazide', 1, 'tablet', 'DA', diag_id)
            elif record.bp <= 114:
                sev = 'MI' if record.bp > 104 else 'MO'
                diag_id = create_diagnosis(patient, 'Hypotension', sev, 'low blood pressure', 'CV', False, record)
                create_treatment(patient, 'Carvedilol', 2, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Fludrocortisone', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Midodrine', 1, 'tablet', 'DA', diag_id)
            elif record.st_depression > 2.3:
                diag_id = create_diagnosis(patient, 'Coronary Artery Disease', 'SE', 'arteries that supply blood to the heart become narrowed or blocked due to atherosclerosis', 'CV', False, record)
                create_treatment(patient, 'Atorvastatin', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Aspirin', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Clopidogrel', 1, 'tablet', 'DA', diag_id)
            elif record.st_depression > 2.1:
                diag_id = create_diagnosis(patient, 'Myocarditis', 'MO', 'inflammation of the heart muscle', 'CV', False, record)
                create_treatment(patient, 'Metoprolol', 3, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Prednisone', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Azathioprine', 1, 'tablet', 'DA', diag_id)
            elif record.st_depression < 0.7 and record.type_of_pain != 'NP':
                diag_id = create_diagnosis(patient, 'Unstable angina', 'MI', 'discomfort caused by reduced blood flow to the heart muscle', 'CV', False, record)
                create_treatment(patient, 'Amlodipine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Nitroglycerin', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Metoprolol', 1, 'tablet', 'DA', diag_id)
            elif record.type_of_pain != 'NP' and random.random() < 0.6:
                diag_id = create_diagnosis(patient, 'Angina', 'MI', 'heart muscle doesn\'t receive enough oxygen-rich blood', 'CV', False, record)
                create_treatment(patient, 'Amlodipine', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Nitroglycerin', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Metoprolol', 1, 'tablet', 'DA', diag_id)
            elif record.maxhr >= 195:
                diag_id = create_diagnosis(patient, 'Atrial Fibrillation', 'SE', 'irregular heart rhythm characterized by rapid and irregular beating of the atria', 'CV', False, record)
                create_treatment(patient, 'Warfarin', 2, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Diltiazem', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Digoxin', 1, 'tablet', 'DA', diag_id)
            elif record.fluoroscopy_vessels > 0:
                diag_id = create_diagnosis(patient, 'Coronary Artery Disease', 'SE', 'major vessels show blockages or narrowing', 'CV', False, record)
                create_treatment(patient, 'Aspirin', 3, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Clopidogrel', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Atorvastatin', 1, 'tablet', 'DA', diag_id)

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientAnalysisCardiologist model.'))