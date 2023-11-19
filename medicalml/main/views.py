from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate

from .forms import PhysicianForm
from .models import PatientBaseRecord, PatientAnalysisPhysician
from django.contrib.auth.models import User

from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods



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
def add_record(request, record_id):
    patient_record = get_object_or_404(PatientBaseRecord, pk=record_id)
    current_user = get_object_or_404(User, pk=request.user.pk)

    if request.method == 'POST':
        form = PhysicianForm(request.POST)
        if form.is_valid():
            physician_record = form.save(commit=False)
            physician_record.patient = patient_record
            physician_record.doctor = current_user
            physician_record.save()
            return redirect('detailed_view_record', record_id=patient_record.id)
    else:
        form = PhysicianForm()
        return render(request, 'main/add_record.html', {'form': form})


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
    record = get_object_or_404(PatientBaseRecord, pk=record_id)
    physician = PatientAnalysisPhysician.objects.filter(patient=record.pk)
    return render(request, 'main/detailed_view_record.html', {'record': record, 'physician': physician})

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