import os
import pickle
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import numpy as np

from main.templatetags.medicalml_extras import tag_definition
from .forms import BodyFatTestForm, DermatologyTestForm, RecordForm, RegisterForm, ThyroidTestForm
from django.contrib.auth import login, logout, authenticate

from .forms import CardiologistForm, BloodTestForm, DiagnosisForm, TreatmentForm, ExaminationsForm
from .models import PatientBaseRecord, DoctorBaseRecord, PatientAnalysisCardiologist, PatientBloodTest, PatientBodyFatTest, PatientDermatologyTest, PatientDiagnosis, PatientThyroidTest, PatientTreatment, ModelPrediction
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
    """
    Redirects the user based on their authentication status and role.

    Args:
        request: The HTTP request object.

    Returns:
        Redirects the user to the home page if they are a doctor.
        Redirects the user to their detailed record view if they are not a doctor.
        Redirects unauthenticated users to the login page.
    """
    if request.user.is_authenticated:
        if check_user_login(request) == 'doctor':
            return redirect(reverse('home'))
        else:
            return redirect(reverse('detailed_view_record', args=[request.user.id]))
    else:
        return redirect('login')


@login_required(login_url='/login')
def home(request):
    """
    Renders the home page with a list of patient records for doctors.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template with patient records, search query, and doctor information.
        Or, returns a forbidden response if the logged-in user is not a doctor.
    """
    if check_user_login(request) == 'doctor':
        doctor = DoctorBaseRecord.objects.filter(doctor=request.user).first()
        query = request.GET.get('q')
        if query:
            records = PatientBaseRecord.objects.filter(
                models.Q(first_name__icontains=query) | models.Q(last_name__icontains=query) | models.Q(id__icontains=query)
            )
        else:
            records = PatientBaseRecord.objects.all()

        records_per_page = 6

        paginator = Paginator(records, records_per_page)
        page = request.GET.get('page')

        try:
            records = paginator.page(page)
        except PageNotAnInteger:
            records = paginator.page(1)
        except EmptyPage:
            records = paginator.page(paginator.num_pages)

        return render(request, 'main/home.html', {'records': records, 'query': query, 'doctor': doctor})
    elif check_user_login(request) == 'patient':
         return redirect(reverse('detailed_view_record', args=[request.user.id]))
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))   


def get_form_class(test_type):
    form_classes = {
        'PatientCardiologist': CardiologistForm,
        'PatientBlood': BloodTestForm,
        'PatientThyroid': ThyroidTestForm,
        'PatientDermatology': DermatologyTestForm,
        'PatientBodyFat': BodyFatTestForm,

        'PatientDiagnosis': DiagnosisForm,
        'PatientTreatment': TreatmentForm,
    }
    
    return form_classes.get(test_type, CardiologistForm) 

from .models import PatientBaseRecord, PatientAnalysisCardiologist, PatientBloodTest, PatientDiagnosis, PatientTreatment

def get_model_class(model_name):
    form_classes = {
        'PatientCardiologist': PatientAnalysisCardiologist,
        'PatientBlood': PatientBloodTest,
        'PatientDiagnosis': PatientDiagnosis,
        'PatientTreatment': PatientTreatment,
        'PatientBaseRecord': PatientBaseRecord,
        'PatientThyroid': PatientThyroidTest,
        'PatientDermatology': PatientDermatologyTest,
        'PatientBodyFat': PatientBodyFatTest
    }
    
    return form_classes.get(model_name, PatientBaseRecord) 



def sign_up(request):
    """
    Handles user registration and creates a corresponding PatientBaseRecord.

    Args:
        request: The HTTP request object.

    Returns:
        If the request method is POST and the form is valid:
            Creates a new user and a corresponding PatientBaseRecord.
            Logs in the user.
            Redirects to the detailed view record page for the newly created user.
        If the request method is GET or the form is not valid:
            Renders the sign-up form.

    """

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid() and form.cleaned_data['agree_to_terms']:
            user = form.save(commit=True)
            PatientBaseRecord.objects.create(
                id=user.id,
                patient = get_object_or_404(User, pk=user.id),
                first_name='fill in',
                last_name='fill in',
                age=0,
                date_of_birth=datetime.datetime.now(),
                gender='M',
                contact_number='fill in',
                emergency_contact_number='not set',
                emergency_contact_first_name='not set',
                emergency_contact_last_name='not set',
                emergency_contact_relationship='not set',
                allergies='None',
                chronic_diseases='None',
                primary_doctor='None',
                notes='',
            )
            login(request, user)
            return redirect(reverse('detailed_view_record', args=[user.id]))
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {'form': form})



def terms_and_conditions(request):
    return render(request, 'main/terms_and_conditions.html')


@login_required(login_url='/login')
def detailed_view_record(request, record_id):
    """
    Renders the detailed view record page for a patient.

    Args:
        request: The HTTP request object.
        record_id: The ID of the patient's record.

    Returns:
        If the user has the correct permissions:
            Renders the detailed view record page with information about the patient,
            medical examinations, diagnoses, treatments, and model predictions.
        If the user does not have the correct permissions:
            Renders the forbidden page.

    """
    if check_user_page(request, record_id)  == 'doctor' or check_user_page(request, record_id) == 'patient':

        status = check_user_page(request, record_id)

        patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)

        cardiologist_examinations = PatientAnalysisCardiologist.objects.filter(patient=patient_record.pk)
        blood_tests = PatientBloodTest.objects.filter(patient=patient_record.pk)
        thyroid_tests = PatientThyroidTest.objects.filter(patient=patient_record.pk)
        derm_tests = PatientDermatologyTest.objects.filter(patient=patient_record.pk)
        bodyfat_tests = PatientBodyFatTest.objects.filter(patient=patient_record.pk)
        unsorted_medical_examinations = list(chain(cardiologist_examinations, blood_tests,
                                                   thyroid_tests, derm_tests, bodyfat_tests))
        medical_examinations = sorted(unsorted_medical_examinations, key=attrgetter('date'), reverse=True)

        patient_diagnoses = sorted(PatientDiagnosis.objects.filter(patient=patient_record.pk), key=attrgetter('date'), reverse=True)

        patient_treatments = sorted(PatientTreatment.objects.filter(patient=patient_record.pk), key=attrgetter('date'), reverse=True)

        model_predictions = sorted(ModelPrediction.objects.filter(patient=patient_record.pk), key=attrgetter('time'), reverse=True)

        return render(request, 'main/detailed_view_record.html', {
            'record': patient_record,
            'medical_examinations': medical_examinations,
            'patient_diagnoses': patient_diagnoses,
            'patient_treatments': patient_treatments,
            'model_predictions': model_predictions,
            'status': status
            })
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))  





@login_required(login_url='/login')
@require_http_methods(["GET", "POST"])
def edit_profile(request, record_id):
    """
    Renders the edit record page for a patient and handles the form submission.

    Args:
        request: The HTTP request object.
        record_id: The ID of the patient's record.

    Returns:
        If the user has the correct permissions:
            - GET: Renders the edit record page with the pre-filled form.
            - POST: Processes the form submission, updates the record, and redirects to the home page.
        If the user does not have the correct permissions:
            Renders the forbidden page.

    """
    if check_user_page(request, record_id) == 'doctor' or check_user_page(request, record_id)  == 'patient':
        record = get_object_or_404(PatientBaseRecord, pk=record_id)
        status = check_user_page(request, record_id)

        if request.method == "POST":
            form = RecordForm(request.POST, instance=record)
            if form.is_valid():
                form.save()
                return redirect('/home')  # Replace with the appropriate success URL
        else:
            form = RecordForm(instance=record)

        return render(request, "main/edit_record.html", {"form": form, "record": record, "status": status, 'page': 'profile'})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))    
    
@login_required(login_url='/login')
def edit_record(request, record_id, exam_type, id):
    
    status = check_user_page(request, record_id)

    record = get_object_or_404(get_model_class(exam_type), pk=id)
    form_class = get_form_class(exam_type)

    if request.method == "POST":
        form = form_class(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.save()
            return redirect('detailed_view_record', record_id=record_id)  # Replace with the appropriate success URL
    else:
        form = form_class(instance=record)
    return render(request, "main/edit_record.html", {"form": form, "record": record, "status": status})



@login_required(login_url='/login')
def delete_record(request, record_id, exam_type, id):
    record = get_object_or_404(get_model_class(exam_type), id=id)
    if request.method == 'POST':
        record.delete()
        return redirect('detailed_view_record', record_id=record_id)  
    return redirect('detailed_view_record', record_id=record_id)


@login_required(login_url='/login')
def add_record(request, record_id, test_type):
    """
    Renders the add record page for a doctor and handles the form submission.

    Args:
        request: The HTTP request object.
        record_id: The ID of the patient's record.
        test_type: The type of medical test or treatment to add.

    Returns:
        If the user is a doctor:
            - GET: Renders the add record page with the appropriate form.
            - POST: Processes the form submission, creates the medical record, and redirects to the detailed view page.
        If the user is not a doctor:
            Renders the forbidden page.

    """
    if check_user_page(request, record_id) == 'doctor':
        patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
        current_user = get_object_or_404(DoctorBaseRecord, pk=request.user.pk)

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
            if test_type == 'PatientTreatment':
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
    """
    Renders the page for updating examinations attached to a patient's diagnosis
    and handles the form submission.

    Args:
        request: The HTTP request object.
        record_id: The ID of the patient's record.
        diagnosis_id: The ID of the patient's diagnosis.

    Returns:
        If the user is a doctor:
            - GET: Renders the update examinations page with the appropriate form and available medical examinations.
            - POST: Processes the form submission, updates the examinations, and redirects to the detailed view page.
        If the user is not a doctor:
            Renders the forbidden page.
    """
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
            cardiologist_examinations = PatientAnalysisCardiologist.objects.filter(patient=patient_record.pk)
            blood_tests = PatientBloodTest.objects.filter(patient=patient_record.pk)
            thyroid_tests = PatientThyroidTest.objects.filter(patient=patient_record.pk)
            derm_tests = PatientDermatologyTest.objects.filter(patient=patient_record.pk)
            bodyfat_tests = PatientBodyFatTest.objects.filter(patient=patient_record.pk)
            unsorted_medical_examinations = list(chain(cardiologist_examinations, blood_tests, thyroid_tests, derm_tests, bodyfat_tests))
            medical_examinations = sorted(unsorted_medical_examinations, key=attrgetter('date'), reverse=True)
            
            filtered_medical_examinations = [exam for exam in medical_examinations if exam.shortened_id not in present_exams_shortened_ids]
            dynamic_html_content = ''
            for exam in filtered_medical_examinations:
                if exam.get_model_type() == "PatientAnalysisCardiologist":
                    dynamic_html_content += f'''  
                        <div class="card mt-2"  id="examination_{{exam.shortened_id}}">
                            <div class="card-body d-flex flex-row justify-content-between">
                                <div>
                                    <h5 class="card-title">Cardiologist test #{exam.shortened_id}</h5>
                                    <p><strong>date:</strong> {exam.date}</p>
                                    <p><strong>Blood Pressure:</strong> {exam.bp}</p>
                                    <p><strong>Type of pain:</strong> {exam.type_of_pain}</p>
                                </div>
                            </div>
                        </div>'''
                elif exam.get_model_type() == "PatientBlood":
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
                elif exam.get_model_type() == "PatientBodyFat":
                    dynamic_html_content += f'''    
                        <div class="card mt-2" id="examination_{exam.shortened_id}">
                        <div class="card-body">
                            <div>
                                <h5 class="card-title">Body measures test #{exam.shortened_id}</h5> 
                                <p><strong>date:</strong> {exam.date}</p>
                                <p><strong>height:</strong> {exam.height}</p>
                                <p><strong>weight:</strong> {exam.weight}/p>
                                <p><strong>chest_circ:</strong> {exam.chest_circ}
                                </p>
                            </div>
                        </div>
                    </div>'''
                elif exam.get_model_type() == "PatientThyroid":
                    dynamic_html_content += f'''    
                        <div class="card mt-2" id="examination_{exam.shortened_id}">
                        <div class="card-body">
                            <div>
                                <h5 class="card-title">Thyroid test #{exam.shortened_id}</h5> 
                                <p><strong>date:</strong> {exam.date}</p>
                                <p><strong>tsh:</strong> {exam.tsh}</p>
                                <p><strong>t3:</strong> {exam.t3}</p>
                                <p><strong>tt4:</strong> {exam.tt4}</p>
                            </div>
                        </div>
                    </div>'''
                elif exam.get_model_type() == "PatientDermatology":
                    dynamic_html_content += f'''    
                        <div class="card mt-2" id="examination_{exam.shortened_id}">
                        <div class="card-body">
                            <div>
                                <h5 class="card-title">Dermatology test #{exam.shortened_id}</h5> 
                                <p><strong>date:</strong> {exam.date}</p>
                                <p><strong>scaling:</strong> {exam.scaling}</p>
                                <p><strong>definite_borders:</strong> {exam.definite_borders}</p>
                                <p><strong>itching:</strong> {exam.itching}</p>
                            </div>
                        </div>
                    </div>'''
            return render(request, 'main/add_record.html', {'form': form,
                                                            'dynamic_html_content': dynamic_html_content
                                                            })
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))  





@login_required(login_url='/login')
def predict_blood_view(request, record_id):
    if check_user_page(request, record_id)  == 'doctor':
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'rfm_bt.pkl')
        scaler_path = os.path.join(os.path.dirname(__file__), 'model', 'scaler_bt.pkl')

        with open(model_path, 'rb') as file, open(scaler_path, 'rb') as scaler:
            loaded_model = pickle.load(file)
            loaded_scaler = pickle.load(scaler)
            patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
            blood_test = PatientBloodTest.objects.filter(patient=patient_record.pk).order_by('date').last()

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
            predicted_class = loaded_model.predict(df)
            predictions_proba = loaded_model.predict_proba(df)[0, predicted_class]

            reverse_mapping = {
                "0": "None",
                "1": "Posssibly none",
                "2": "Hepatitis",
                "3": "Fibrosis",
                "4": "Cirrhosis"
            }
            df = loaded_scaler.transform(df)
            predicted_class = loaded_model.predict(df)
            predicted_class_reversed = [reverse_mapping[str(label)] for label in predicted_class]

            predictions = {
                'predicted_class_num':predicted_class,
                'predicted_class_text':predicted_class_reversed[0],
                'predictions_proba':predictions_proba[0]
            }

            ModelPrediction.objects.create(
                patient = patient_record,
                modelname = 'Blood test',
                time = datetime.datetime.now(),
                predicted_class = predicted_class,
                class_text = predicted_class_reversed[0],
                certainty = predictions_proba[0]
            )

            print(predictions)
            return render(request, 'main/results.html', {'record': patient_record, 'prediction': predictions})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))    


@login_required(login_url='/login')
def predict_cardio_view(request, record_id):
    if check_user_page(request, record_id)  == 'doctor':
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'ann_heart.pkl')

        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)
            patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
            cardio_test = PatientAnalysisCardiologist.objects.filter(patient=patient_record.pk).order_by('date').last()
            blood_test = PatientBloodTest.objects.filter(patient=patient_record.pk).order_by('date').last()

            data = {
                'Age': [patient_record.age],
                'Sex': [patient_record.gender],
                'Chest pain type': [cardio_test.type_of_pain if cardio_test else None],
                'BP': [cardio_test.bp if cardio_test else None],
                'FBS over 120': [blood_test.bg if blood_test else None],
                'Cholesterol': [blood_test.chol if blood_test else None],
                'EKG results': [cardio_test.resting_ecg if cardio_test else None],
                'Max HR': [cardio_test.maxhr if cardio_test else None],
                'Exercise angina': [bool(cardio_test.excercise_angina) if cardio_test else None],
                'ST depression': [int(cardio_test.st_depression) if cardio_test else None],
                'Slope of ST': [cardio_test.slope_st if cardio_test else None],
                'Number of vessels fluro': [cardio_test.fluoroscopy_vessels if cardio_test else None],
            }


            df = pd.DataFrame(data)
            df.replace('M', 0, inplace=True)
            df.replace('F', 1, inplace=True)

            df.replace('Normal', 0, inplace=True)
            df.replace('ST', 1, inplace=True)
            df.replace('LVH', 2, inplace=True)

            df.replace('Up', 1, inplace=True)
            df.replace('Flat', 2, inplace=True)
            df.replace('Down', 3, inplace=True)

            df.replace('TA', 1, inplace=True)
            df.replace('ATA', 2, inplace=True)
            df.replace('NAP', 3, inplace=True)
            df.replace('ASY', 4, inplace=True)
    

            df['FBS over 120'] = df['FBS over 120'].apply(lambda x: 1 if x > 120 else 0)
            df['Exercise angina'] = df['Exercise angina'].apply(lambda x: 1 if x == True else 0)
            
            [print(i.shape, i.dtype) for i in loaded_model.inputs]
            [print(o.shape, o.dtype) for o in loaded_model.outputs]
            [print(l.name, l.input_shape, l.dtype) for l in loaded_model.layers]

            print(df.head())
            print(df.dtypes)
            print(df.values)
            predicted_class = loaded_model.predict(df)

            print(df.head())
            x = np.asarray(df).astype(int)
            predicted_class_proba = loaded_model.predict(x)

            predicted_class_num = (predicted_class > 0.5)
            if predicted_class_num:
                predicted_class_text = 'possible disorder'
            else:
                predicted_class_text = 'absence of disorder'


            predictions = {
                'predicted_class_num':predicted_class_num,
                'predicted_class_text': predicted_class_text[0],
                'predictions_proba':predicted_class_proba[0]
            }

            ModelPrediction.objects.create(
                patient = patient_record,
                modelname = "Cardio",
                time = datetime.datetime.now(),
                predicted_class = predicted_class_num,
                class_text = predicted_class_text[0],
                certainty = predicted_class_proba[0]
            )

            print(predictions)
            return render(request, 'main/results.html', {'record': patient_record, 'prediction': predictions})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))      



@login_required(login_url='/login')
def predict_thyroid_view(request, record_id):
    if check_user_page(request, record_id)  == 'doctor':
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'xgb_thyroid.pkl')

        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)
            patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
            thyroid_test = PatientThyroidTest.objects.filter(patient=patient_record.pk).order_by('date').last()

            data = {
                'T3': [float(thyroid_test.t3) if thyroid_test else None],
                'TSH': [float(thyroid_test.tsh) if thyroid_test else None],
                'FTI': [float(thyroid_test.fti) if thyroid_test else None],
                'T4U': [float(thyroid_test.t4u) if thyroid_test else None],
                'TT4': [float(thyroid_test.tt4)if thyroid_test else None],
                'goitre': [bool(thyroid_test.goitre) if thyroid_test else None],
                'sex': [patient_record.gender],
                'age': [patient_record.age],
            }

            df = pd.DataFrame(data)
            df.replace('M', 0, inplace=True)
            df.replace('F', 1, inplace=True)
            predicted_class = loaded_model.predict(df)
            predictions_proba = loaded_model.predict_proba(df)[0, predicted_class]

            print(df.head())

            reverse_mapping = {
                "0": "Negative",
                "1": "Hypothyroid",
                "2": "Hyperthyroid"
            }

            predicted_class = loaded_model.predict(df)
            predicted_class_reversed = [reverse_mapping[str(label)] for label in predicted_class]

            predictions = {
                'predicted_class_num':predicted_class,
                'predicted_class_text':predicted_class_reversed[0],
                'predictions_proba':predictions_proba[0]
            }

            ModelPrediction.objects.create(
                patient = patient_record,
                modelname = 'Thyroid',
                time = datetime.datetime.now(),
                predicted_class = predicted_class,
                class_text = predicted_class_reversed[0],
                certainty = predictions_proba[0]
            )

            print(predictions)
            return render(request, 'main/results.html', {'record': patient_record, 'prediction': predictions})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))      



@login_required(login_url='/login')
def predict_body_fat_view(request, record_id):
    if check_user_page(request, record_id)  == 'doctor':
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'rfr_bf.pkl')
        scaler_path = os.path.join(os.path.dirname(__file__), 'model', 'scaler_bf.pkl')

        with open(model_path, 'rb') as file, open(scaler_path, 'rb') as scaler:
            loaded_model = pickle.load(file)
            loaded_scaler = pickle.load(scaler)
            patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
            bodyfat_test = PatientBodyFatTest.objects.filter(patient=patient_record.pk).order_by('date').last()

            data = {
                'Sex': [patient_record.gender],
                'Age': [patient_record.age],
                'Weight': [float(bodyfat_test.weight) if bodyfat_test else None],
                'Height': [float(bodyfat_test.height) if bodyfat_test else None],
                'Neck': [float(bodyfat_test.neck_circ) if bodyfat_test else None],
                'Chest': [float(bodyfat_test.chest_circ) if bodyfat_test else None],
                'Abdomen': [float(bodyfat_test.abdomen_circ) if bodyfat_test else None],
                'Hip': [float(bodyfat_test.hip_circ) if bodyfat_test else None],
                'Thigh': [float(bodyfat_test.thigh_circ) if bodyfat_test else None],
                'Knee': [float(bodyfat_test.knee_circ) if bodyfat_test else None],
                'Ankle': [float(bodyfat_test.ankle_cirk) if bodyfat_test else None],
                'Biceps': [float(bodyfat_test.bicep_circ) if bodyfat_test else None],
                'Forearm': [float(bodyfat_test.forearm_circ) if bodyfat_test else None],
                'Wrist': [float(bodyfat_test.wrist_circ) if bodyfat_test else None],
            }

            df = pd.DataFrame(data)
            sex_mapping = {'M': 1, 'F': 0}
            df['Sex'] = df['Sex'].map(sex_mapping)
            df_scaled = loaded_scaler.transform(df)
            predicted_class = loaded_model.predict(df_scaled)
            #predictions_proba = loaded_model.predict_proba(df)[0, predicted_class]

            print(df.head())

            predictions = {
                'predicted_class_num':predicted_class,
                'predicted_class_text':"percents",
                'predictions_proba':"regression"
            }

            ModelPrediction.objects.create(
                patient = patient_record,
                modelname = "Body Fat",
                time = datetime.datetime.now(),
                predicted_class = predicted_class,
                class_text = "percents",
                certainty = 1
            )

            print(predictions)
            return render(request, 'main/results.html', {'record': patient_record, 'prediction': predictions})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))      



@login_required(login_url='/login')
def predict_derm_view(request, record_id):
    if check_user_page(request, record_id)  == 'doctor':
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'lgbm_derm.pkl')

        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)
            patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
            derm_test = PatientDermatologyTest.objects.filter(patient=patient_record.pk).order_by('date').last()

            data = {
                'family_history': [bool(derm_test.family_history) if derm_test else None],
                'erythema': [int(derm_test.erythema ) if derm_test else None],
                'scaling': [int(derm_test.scaling ) if derm_test else None],
                'definite_borders': [int(derm_test.definite_borders ) if derm_test else None],
                'itching': [int(derm_test.itching ) if derm_test else None],
                'koebner_phenomenon': [int(derm_test.koebner_phenomenon ) if derm_test else None],
                'polygonal_papules': [int(derm_test.polygonal_papules ) if derm_test else None],
                'follicular_papules': [int(derm_test.follicular_papules ) if derm_test else None],
                'oral_mucosal_involvement': [int(derm_test.oral_mucosal_involvement ) if derm_test else None],
                'knee_and_elbow_involvement': [int(derm_test.knee_and_elbow_involvement ) if derm_test else None],
                'scalp_involvement': [int(derm_test.scalp_involvement ) if derm_test else None],
                'melanin_incontinence': [int(derm_test.melanin_incontinence ) if derm_test else None],
                'eosinophils_in_the_infiltrate': [int(derm_test.eosinophils_in_the_infiltrate ) if derm_test else None],
                'PNL_infiltrate': [int(derm_test.PNL_infiltrate ) if derm_test else None],
                'fibrosis_of_the_papillary_dermis': [int(derm_test.fibrosis_of_the_papillary_dermis ) if derm_test else None],
                'exocytosis': [int(derm_test.exocytosis ) if derm_test else None],
                'acanthosis': [int(derm_test.acanthosis ) if derm_test else None],
                'hyperkeratosis': [int(derm_test.hyperkeratosis ) if derm_test else None],
                'parakeratosis': [int(derm_test.parakeratosis ) if derm_test else None],
                'clubbing_of_the_rete_ridges': [int(derm_test.clubbing_of_the_rete_ridges ) if derm_test else None],
                'elongation_of_the_rete_ridges': [int(derm_test.elongation_of_the_rete_ridges ) if derm_test else None],
                'thinning_of_the_suprapapillary_epidermis': [int(derm_test.thinning_of_the_suprapapillary_epidermis ) if derm_test else None],
                'spongiform_pustule': [int(derm_test.spongiform_pustule ) if derm_test else None],
                'munro_microabcess': [int(derm_test.munro_microabcess ) if derm_test else None],
                'focal_hypergranulosis': [int(derm_test.focal_hypergranulosis ) if derm_test else None],
                'disappearance_of_the_granular_layer': [int(derm_test.disappearance_of_the_granular_layer ) if derm_test else None],
                'vacuolisation_and_damage_of_basal_layer': [int(derm_test.vacuolisation_and_damage_of_basal_layer ) if derm_test else None],
                'spongiosis': [int(derm_test.spongiosis ) if derm_test else None],
                'saw_tooth_appearance_of_retes': [int(derm_test.saw_tooth_appearance_of_retes ) if derm_test else None],
                'follicular_horn_plug': [int(derm_test.follicular_horn_plug ) if derm_test else None],
                'perifollicular_parakeratosis': [int(derm_test.perifollicular_parakeratosis ) if derm_test else None],
                'inflammatory_monoluclear_inflitrate': [int(derm_test.inflammatory_monoluclear_inflitrate ) if derm_test else None],
                'band_like_infiltrate': [int(derm_test.band_like_infiltrate ) if derm_test else None],
                'age': [patient_record.age],
            }
            
            df = pd.DataFrame(data)
            print(df.head())

            reverse_mapping = {
                "1": "psoriasis",
                "2": "seborrheic dermatitis",
                "3": "lichen planus",
                "4": "pityriasis rosea",
                "5": "chronic dermatitis",
                "6": "pityriasis trichosanthes",
            }

            predicted_class = loaded_model.predict(df)
            predictions_proba = loaded_model.predict_proba(df)[0, predicted_class]
            predicted_class_reversed = [reverse_mapping[str(label)] for label in predicted_class]

            if predictions_proba < 0.65:
                predicted_class = 0
                predicted_class_reversed = 'Nothing'

            print(df.head())

            predictions = {
                'predicted_class_num':predicted_class,
                'predicted_class_text':predicted_class_reversed[0],
                'predictions_proba':predictions_proba[0]
            }

            ModelPrediction.objects.create(
                patient = patient_record,
                modelname = "Derm",
                time = datetime.datetime.now(),
                predicted_class = predicted_class,
                class_text = predicted_class_reversed[0],
                certainty = predictions_proba[0]
            )

            print(predictions)
            return render(request, 'main/results.html', {'record': patient_record, 'prediction': predictions})
    else:
        return HttpResponseForbidden(render(request, 'main/403.html'))      
