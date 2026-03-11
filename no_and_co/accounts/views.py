from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib import messages
import re
from django.core.mail import send_mail
import random
import time
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, logout, authenticate

email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
username_pattern = r"^[a-zA-Z0-9_]{4,20}$"
User = get_user_model()


@never_cache
def signup(request):
    session_check = request.session.get("signup_values")

    if session_check:
        return redirect("signup-otp-verification")
    else:
        if request.method == "POST":
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]

            if not username or not email or not password or not confirm_password:
                messages.error(request, "All fields are required")
                return redirect("signup")

            if not re.match(username_pattern, username):
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

            if User.objects.filter(username=username).exists():
                messages.error(request, "Full Name Already Exists")
                return redirect("signup")

            request.session["signup_values"] = {
                "username": username,
                "email": email,
                "password": password,
            }

            otp = random.randint(100000, 999999)
            otp_created_time = time.time()

            request.session["otp"] = otp
            request.session["email"] = email
            if otp_created_time:
                request.session["otp_created_time"] = otp_created_time
            else:
                request.session["otp_created_time"] = 0

            request.session["otp_count"] = 0

            send_mail(
                "Email verification OTP",
                f"Your OTP to sign up is {otp}",
                "waseemfaris@gmail.com",
                [email],
                fail_silently=False,
            )

            messages.success(request, "otp successfully send to mail")
            return redirect("signup-otp-verification")

    return render(request, "signup.html")


def login_user(request):

    if request.method == "POST":

        username = request.POST["username"].strip()
        password = request.POST["password"]

        if not username or not password:
            messages.error(request, "All fields are required")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "login succesfuly")
            return redirect("home")
        else:
            messages.error(request, "invalid username or password")
            return redirect("login")

    return render(request, "login.html")


@never_cache
def signup_otp_verification(request):

    otp_created_time = request.session["otp_created_time"]

    remaining = 0

    if otp_created_time:
        remaining = 60 - int(time.time() - otp_created_time)

        if remaining < 0:
            remaining = 0

    if request.method == "POST":
        user_otp = request.POST["otp"]
        otp = request.session["otp"]

        if str(user_otp) == str(otp):
            signup_data = request.session.get("signup_values")

            username = signup_data["username"]
            email = signup_data["email"]
            password = signup_data["password"]

            User.objects.create_user(username=username, email=email, password=password)

            messages.success(request, "Account created successfully")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP")
            return redirect("signup-otp-verification")

    return render(request, "signup-otp-verification.html", {"remaining_seconds": remaining})


def resend_otp_verification(request):
    if request.method == "POST":
        otp_count = request.session.get("otp_count", 0)

        if otp_count >= 3:
            messages.error(request, "resend limit completed")
            return redirect("otp-verification")
        else:
            otp = random.randint(100000, 999999)
            request.session["otp"] = otp
            request.session["otp_created_time"] = time.time()
            email = request.session["signup_values"]["email"]

            send_mail(
                "Resend Email verification OTP",
                f"Your OTP to sign up is {otp}",
                "waseemfaris@gmail.com",
                [email],
                fail_silently=False,
            )

            otp_count += 1
            request.session["otp_count"] = otp_count

            messages.success(request, "OTP resent successfully")
            return redirect("signup-otp-verification")


def cancel_otp_verification(request):
    if request.method == "POST":
        request.session.flush()
        messages.success(request, "otp verification failed")
        return redirect("signup")


def forgot_password(request):
    if request.method == "POST":

        email = request.POST.get("email")

        if not email:
            messages.error(request, "please fill form to continue")

            return redirect("forgot-password")

        if User.objects.filter(email=email).exists():

            otp = random.randint(100000, 999999)

            request.session["otp"] = otp
            request.session["email"] = email

            send_mail(
                "Resend Email verification OTP",
                f"Your OTP to sign up is {otp}",
                "waseemfaris@gmail.com",
                [email],
                fail_silently=False,
            )

            print(otp)

            messages.success(request, "otp send succesfully")
            return redirect("forgot_password-otp-verification")
        else:
            messages.error(request, "invalid email")
            return redirect("forgot-password")

    return render(request, "forgot-password.html")

def forgot_password_otp_verification(request):

    if request.method == "POST":

        otp = request.POST.get("otp")
        session_otp = request.session["otp"]

        if not otp:
            return redirect(request, "enter a otp to reset password")

        if str(otp)==str(session_otp):
            messages.success(request, "otp verification succesfully")
            return redirect("reset-password")
        else:
            messages.error(request, "invalid otp")
            return redirect("reset-password")

    return render(request,"forgot-password-otp-verification.html")

def reset_password(request):
    return render(request, "reset-password.html")


def logout_user(request):

    logout(request)
    messages.success(request, "logged out successfully")

    return redirect("home")
