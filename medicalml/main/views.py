from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate

from .forms import RecordForm

from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='/login')
def home(request):
    return render(request, 'main/home.html')


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