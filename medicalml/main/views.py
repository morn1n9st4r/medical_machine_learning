from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate

from .forms import PhysicianForm, BloodTestForm, DiagnosisForm, TreatmentForm, ExaminationsForm
from .models import PatientBaseRecord, PatientAnalysisPhysician, PatientBloodTest, PatientDiagnosis, PatientTreatment
from django.contrib.auth.models import User

from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from itertools import chain
from operator import attrgetter

import datetime

@login_required(login_url='/login')
def home(request):
    records = PatientBaseRecord.objects.all()

    # DELETION SEQUENCE
    #if request.method == 'POST':
    #    record_id = request.POST.get('record-id')
    #    record = PatientBaseRecord.objects.filter(pk=record_id).first()
    #    if record and record.author == request.user:
    #        record.delete()

    return render(request, 'main/home.html', {'records': records})


@login_required(login_url='/login')
def add_record(request, record_id, test_type):
    patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
    current_user = get_object_or_404(User, pk=request.user.pk)

    form_class = get_form_class(test_type)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.patient = patient_record
            medical_record.doctor = current_user
            medical_record.date = datetime.datetime.now()

            medical_record.save()
            return redirect('detailed_view_record', record_id=patient_record.id)
    else:
        form = form_class(record_id=record_id)
        return render(request, 'main/add_record.html', {'form': form})



@login_required(login_url='/login')
def update_examinations(request, record_id, diagnosis_id):
    patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
    patient_diagnosis = get_object_or_404(PatientDiagnosis, pk=diagnosis_id)

    if request.method == 'POST':
        form = ExaminationsForm(request.POST)
        if form.is_valid():
            updated_examinations = form.cleaned_data['examinations']

            # split and check all already attached and prohibit duplicate
            if patient_diagnosis.examinations == "":
                patient_diagnosis.examinations += updated_examinations
            else:
                patient_diagnosis.examinations += ", " + updated_examinations
            
            patient_diagnosis.save()
            return redirect('detailed_view_record', record_id=patient_record.id)  # Replace with the appropriate redirect
    else:
        form = ExaminationsForm()

        # add html's to template from view???

        return render(request, 'main/add_record.html', {'form': form})


def get_form_class(test_type):
    form_classes = {
        'physician': PhysicianForm,
        'blood_test': BloodTestForm,

        'diagnosis': DiagnosisForm,
        'treatment': TreatmentForm,
    }
    
    return form_classes.get(test_type, PhysicianForm) 


# sign up with email, not username
def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {'form': form})

@login_required(login_url='/login')
def detailed_view_record(request, record_id):
    patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)

    physician_examinations = PatientAnalysisPhysician.objects.filter(patient=patient_record.pk)
    blood_tests = PatientBloodTest.objects.filter(patient=patient_record.pk)
    unsorted_medical_examinations = list(chain(physician_examinations, blood_tests))
    medical_examinations = sorted(unsorted_medical_examinations, key=attrgetter('date'), reverse=True)

    patient_diagnoses = PatientDiagnosis.objects.filter(patient=patient_record.pk)

    patient_treatments = PatientTreatment.objects.filter(patient=patient_record.pk)

    return render(request, 'main/detailed_view_record.html', {
        'record': patient_record,
        'medical_examinations': medical_examinations,
        'patient_diagnoses': patient_diagnoses,
        'patient_treatments': patient_treatments,
        })

#@login_required(login_url='/login')
#@require_http_methods(["GET", "POST"])
#def update_record(request, pk):
#    record = get_object_or_404(PatientBaseRecord, pk=pk)
#
#    if request.method == "POST":
#        form = RecordForm(request.POST, instance=record)
#        if form.is_valid():
#            form.save()
#            return redirect('/home')  # Replace with the appropriate success URL
#    else:
#        form = RecordForm(instance=record)
#
#    return render(request, "main/update_record.html", {"form": form, "record": record})