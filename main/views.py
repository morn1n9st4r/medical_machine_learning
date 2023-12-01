import os
import pickle
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from main.templatetags.medicalml_extras import tag_definition
from .forms import RecordForm, RegisterForm
from django.contrib.auth import login, logout, authenticate

from .forms import PhysicianForm, BloodTestForm, DiagnosisForm, TreatmentForm, ExaminationsForm
from .models import PatientBaseRecord, DoctorBaseRecord, PatientAnalysisPhysician, PatientBloodTest, PatientDiagnosis, PatientTreatment
from django.contrib.auth.models import User

from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from itertools import chain
from operator import attrgetter

import datetime
import pandas as pd

from django.db import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def check_user_page(req, record_id):
    patients = PatientBaseRecord.objects.filter(patient=req.user).first()
    if patients:
        if req.user.id == record_id:
            return 'patient'
        else:
            return 'forbidden'
    else:
        return 'doctor'



def check_user_login(req):
    patients = PatientBaseRecord.objects.filter(patient=req.user).first()
    if patients:
        return 'patient'
    else:
        return 'doctor'



@login_required(login_url='/login')
def custom_login_redirect(request):
    if request.user.is_authenticated:
        if check_user_login(request) == 'doctor':
            return redirect(reverse('home'))
        else:
            return redirect(reverse('detailed_view_record', args=[request.user.id]))
    else:
        return redirect('login')


@login_required(login_url='/login')
def home(request):
    if check_user_login(request) == 'doctor':
        doctor = DoctorBaseRecord.objects.filter(doctor=request.user).first()
        query = request.GET.get('q')
        if query:
            records = PatientBaseRecord.objects.filter(
                models.Q(first_name__icontains=query) | models.Q(last_name__icontains=query)
            )
        else:
            records = PatientBaseRecord.objects.all()

        records_per_page = 10

        paginator = Paginator(records, records_per_page)
        page = request.GET.get('page')

        try:
            records = paginator.page(page)
        except PageNotAnInteger:
            records = paginator.page(1)
        except EmptyPage:
            records = paginator.page(paginator.num_pages)

        return render(request, 'main/home.html', {'records': records, 'query': query, 'doctor': doctor})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))   


@login_required(login_url='/login')
def add_record(request, record_id, test_type):
    if check_user_page(request, record_id) == 'doctor':
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
            form = form_class()

            dynamic_html_content = ''
            if test_type == 'treatment':
                patient_diagnoses = PatientDiagnosis.objects.filter(patient=patient_record.pk)
                for diagnosis in patient_diagnoses:
                    dynamic_html_content += f'''
                        <div class="card mt-2" id="diagnosis_{diagnosis.shortened_id}">
                            <div class="card-body d-flex flex-row justify-content-between">
                                <div>
                                    <h5 class="card-title">Diagnosis #{diagnosis.shortened_id}</h5>
                                    <p><strong>date:</strong> {diagnosis.date}</p>
                                    <p><strong>disease_name:</strong> {diagnosis.disease_name}</p>
                                    <p><strong>severity:</strong> {diagnosis.severity}</p>
                                    <p><strong>tag:</strong> {diagnosis.tags}</p>
                                    <p><strong>details:</strong> {diagnosis.details}</p>
                                </div>
                            </div>
                        </div>
                    '''
            return render(request, 'main/add_record.html', {'form': form,
                                                            'dynamic_html_content': dynamic_html_content,
                                                            })
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))    





@login_required(login_url='/login')
def update_examinations(request, record_id, diagnosis_id):
    if check_user_page(request, record_id)  == 'doctor':
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

            present_exams_shortened_ids = patient_diagnosis.examinations.split(", ")
            physician_examinations = PatientAnalysisPhysician.objects.filter(patient=patient_record.pk)
            blood_tests = PatientBloodTest.objects.filter(patient=patient_record.pk)
            unsorted_medical_examinations = list(chain(physician_examinations, blood_tests))
            medical_examinations = sorted(unsorted_medical_examinations, key=attrgetter('date'), reverse=True)
            
            filtered_medical_examinations = [exam for exam in medical_examinations if exam.shortened_id not in present_exams_shortened_ids]
            dynamic_html_content = ''
            for exam in filtered_medical_examinations:
                if exam.get_model_type() == "PatientAnalysisPhysician":
                    dynamic_html_content += f'''  
                        <div class="card mt-2"  id="examination_{{exam.shortened_id}}">
                            <div class="card-body d-flex flex-row justify-content-between">
                                <div>
                                    <h5 class="card-title">Physician test #{exam.shortened_id}</h5>
                                    <p><strong>date:</strong> {exam.date}</p>
                                    <p><strong>height:</strong> {exam.height}</p>
                                    <p><strong>weight:</strong> {exam.weight}</p>
                                    <p><strong>Blood Pressure:</strong> {exam.bp}</p>
                                    <p><strong>Type of pain:</strong> {exam.type_of_pain}</p>
                                </div>
                            </div>
                        </div>'''
                else:
                    dynamic_html_content += f'''    
                        <div class="card mt-2"  id="examination_{exam.shortened_id}">
                            <div class="card-body d-flex flex-row justify-content-between">
                                <div>
                                    <h5 class="card-title">Blood test #{exam.shortened_id}</h5>
                                    <p><strong>date:</strong> {exam.date}</p>
                                    <p><strong>alb:</strong> {exam.alb}</p>
                                    <p><strong>chol:</strong> {exam.chol}</p>
                                    <p><strong>prot:</strong> {exam.prot}</p>
                                </div>
                            </div>
                        </div>'''

            return render(request, 'main/add_record.html', {'form': form,
                                                            'dynamic_html_content': dynamic_html_content
                                                            })
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))  



def get_form_class(test_type):
    form_classes = {
        'physician': PhysicianForm,
        'blood_test': BloodTestForm,

        'diagnosis': DiagnosisForm,
        'treatment': TreatmentForm,
    }
    
    return form_classes.get(test_type, PhysicianForm) 




def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            PatientBaseRecord.objects.create(
                id=user.id,
                patient = get_object_or_404(User, pk=user.id),
                first_name='first_name',
                last_name='last_name',
                age=18,
                date_of_birth=datetime.datetime.now(),
                gender='M',
                contact_number='380947100983',
                emergency_contact_number='380947100983',
                emergency_contact_first_name='emergency_contact_first_name',
                emergency_contact_last_name='emergency_contact_last_name',
                emergency_contact_relationship='emergency_contact_relationship',
                allergies='allergies',
                chronic_diseases='chronic_diseases',
                primary_doctor='primary_doctor',
                notes='notes',
            )
            login(request, user)
            return redirect(reverse('detailed_view_record', args=[user.id]))
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {'form': form})





@login_required(login_url='/login')
def detailed_view_record(request, record_id):
    if check_user_page(request, record_id)  == 'doctor' or check_user_page(request, record_id) == 'patient':

        status = check_user_page(request, record_id)

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
            'status': status
            })
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))  




@login_required(login_url='/login')
def run_pkl_view(request, record_id):
    if check_user_page(request, record_id)  == 'doctor':
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'rfm.pkl')

        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)
            patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
            blood_test = PatientBloodTest.objects.filter(patient=patient_record.pk).order_by('date').first()

            data = {
                'Age': [patient_record.age],
                'Sex': [patient_record.gender],
                'ALB': [blood_test.alb if blood_test else None],
                'ALP': [blood_test.alp if blood_test else None],
                'ALT': [blood_test.alt if blood_test else None],
                'AST': [blood_test.ast if blood_test else None],
                'BIL': [blood_test.bil if blood_test else None],
                'CHE': [blood_test.che if blood_test else None],
                'CHOL': [blood_test.chol if blood_test else None],
                'CREA': [blood_test.crea if blood_test else None],
                'GGT': [blood_test.gct if blood_test else None],
                'PROT': [blood_test.prot if blood_test else None],
            }

            df = pd.DataFrame(data)
            df.loc[df["Sex"] == "M", "Sex"] = "1"
            df.loc[df["Sex"] == "F", "Sex"] = "0"
            predictions = loaded_model.predict(df)

            print(predictions)

            return render(request, 'main/results.html', {'record': patient_record, 'predictions': predictions})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))    



@login_required(login_url='/login')
@require_http_methods(["GET", "POST"])
def edit_record(request, record_id):
    if check_user_page(request, record_id) == 'doctor' or check_user_page(request, record_id)  == 'patient':
        record = get_object_or_404(PatientBaseRecord, pk=record_id)

        if request.method == "POST":
            form = RecordForm(request.POST, instance=record)
            if form.is_valid():
                form.save()
                return redirect('/home')  # Replace with the appropriate success URL
        else:
            form = RecordForm(instance=record)

        return render(request, "main/edit_record.html", {"form": form, "record": record})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))    