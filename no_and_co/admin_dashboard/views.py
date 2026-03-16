from django.shortcuts import render,redirect
from accounts.models import User
from django.contrib.auth import login, logout,authenticate
from django.contrib import messages
from django.http import HttpResponse
import random
from django.core.mail import send_mail
import time
# Create your views here.

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(email=email,password=password)

        if user and user.is_superuser:
            login(request, user)
            messages.success(request, "admin login succesfully")
            return redirect("admin-dashboard")
        else:
            if user:
                messages.error(request, "user are not allowed")
                return redirect("login")
            messages.error(request, "invalid username or password")
            return redirect("admin-login")
    return render(request, "admin-login.html")

def admin_dashboard(request):
    return render(request, "admin-dashboard.html")

def admin_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email, is_superuser = True)
            request.session["admin_email"] = email
            otp = random.randint(100000,999999)
            request.session["admin_otp"] = otp
            request.session["admin_otp_created_at"] = time.time()

            send_mail(
                        "Email verification OTP",
                        f"Your OTP to sign up is {otp}",
                        "waseemfaris@gmail.com",
                        [email],
                        fail_silently=False,
                    )

            messages.success(request, "OTP send to mail")
            return redirect("admin-otp-verification")

        except:
            messages.error(request, "Email doesnt found")
            return redirect("admin-forgot-password")

    return render(request, "admin-forgot-pass.html")

def admin_otp_verification(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp_code")
        email = request.session.get("email", None)
        otp = request.session.get("admin_otp",0)

        if not user_otp:
            messages.error(request, "Please fill otp to countinue")
            return redirect("admin-otp-verification")

        if str(user_otp)==str(otp):
            messages.success(request, "otp verify successfuly")
            return redirect("admin-reset-password")
        else:
            messages.error(request, "invalid OTP")
            return redirect("admin-otp-verification")

    return render(request, "admin-otp-verification.html")

def admin_reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        email = request.session.get("email",None)

        if new_password!=confirm_password:
            messages.error(request, "Password doesnt match")
            return redirect("admin-reset-password")

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully")
            return redirect("admin-login")
        except:
            messages.error(request, "Password update failed")
            return redirect("admin-reset-passsword")

    return render(request, "admin-reset-pass.html")
