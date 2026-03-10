from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib import messages
import re
from django.core.mail import send_mail
import random

email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
fullname_pattern = r"^[a-zA-Z0-9_]{4,20}$"


def signup(request):

    User = get_user_model()

    if request.method == "POST":
        full_name = request.POST["full_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if not re.match(fullname_pattern, full_name):
            messages.error(
                request,
                "Invalid Full Name Format",
            )
            return redirect("signup")

        if not re.match(email_pattern, email):
            messages.error(request, "Invalid email address")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "Password Doesnt Match")
            return redirect("signup")

        if not re.match(password_pattern, password):
            messages.error(
                request,
                "Password too weak.",
            )
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Exists")
            return redirect("signup")

        if User.objects.filter(full_name=full_name).exists():
            messages.error(request, "Full Name Already Exists")
            return redirect("signup")

        otp = random.randint(100000, 999999)

        request.session["otp"] = otp
        request.session["email"] = email

        send_mail(
            "Email verification OTP",
            f"Your OTP to sign up is {otp}",
            "waseemfaris@gmail.com",
            [email],
            fail_silently=False,
        )

        messages.success(request, "otp successfully send to mail")
        return redirect("otp-verification")

    return render(request, "signup.html")


def login(request):
    return render(request, "login.html")


def forgot_password(request):
    return render(request, "forgot-password.html")


def otp_verification(request):
    return render(request, "otp-verification.html")


def reset_password(request):
    return render(request, "reset-password.html")
