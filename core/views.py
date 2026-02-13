from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import SOSAlert
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, "index.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password1"]
        confirm_password = request.POST["password2"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "register.html")




def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
    return render(request, "login.html")


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


@login_required
def profile_view(request):
    return render(request, "profile.html")


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        user = request.user
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()
        return redirect("profile")
    
    return render(request, "profile_edit.html")


@login_required
def safe_trips_view(request):
    return render(request, "safe_trips.html")


@login_required
def safety_points_view(request):
    return render(request, "safety_points.html")


@login_required
def sos_view(request):
    if request.method == "POST":
        location = request.POST.get("location")
        SOSAlert.objects.create(user=request.user, location=location)
        return render(request, "sos.html", {"message": "SOS Sent Successfully!"})
    return render(request, "sos.html")


def logout_view(request):
    logout(request)
    return redirect("index")






# Create your views here.
