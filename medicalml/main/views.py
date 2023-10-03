from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate

from .forms import RecordForm
from .models import Record

from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
# Create your views here.


@login_required(login_url='/login')
def home(request):
    records = Record.objects.all()
    return render(request, 'main/home.html', {'records': records})


@login_required(login_url='/login')
def add_record(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.author = request.user
            record.save()
            return redirect('/home')
    else:
        form = RecordForm()
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


#def __str__(self) -> str:
#        return self.patient_name + "\n" + \
#               self.age + "\n" + \
#               self.sex + "\n" + \
#               self.chest_pain_type + "\n" + \
#               self.resting_bp + "\n" + \
#               self.cholesterol + "\n" + \
#               self.fasting_blood_sugar + "\n" + \
#               self.resting_ecg + "\n" + \
#               self.max_heart_rate + "\n" + \
#               self.exercise_angina + "\n" + \
#               self.oldpeak + "\n" + \
#               self.st_slope

@login_required(login_url='/login')
@require_http_methods(["GET", "POST"])
def update_record(request, pk):
    record = get_object_or_404(Record, pk=pk)

    if request.method == "POST":
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('/home')  # Replace with the appropriate success URL
    else:
        form = RecordForm(instance=record)

    return render(request, "main/update_record.html", {"form": form, "record": record})