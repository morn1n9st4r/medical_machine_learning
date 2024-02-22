
from datetime import timedelta
import random
from main.models import DoctorBaseRecord, MedicalRecordRegistry, PatientDiagnosis, PatientTreatment


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

