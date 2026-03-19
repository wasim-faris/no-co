from django.shortcuts import render, redirect
from accounts.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import random
from django.core.mail import send_mail
import time
import re
from django.contrib.auth.hashers import make_password, check_password
from .decorators import admin_required
email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
password_pattern = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.


def no_cache(response):
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

@never_cache
def admin_login(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

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
    return render(request, "account/admin-login.html")

@admin_required
@never_cache
def admin_dashboard(request):

    return render(request, "admin-dashboard.html")

@never_cache
def admin_forgot_password(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email, is_superuser=True)
            request.session["admin_email"] = email
            otp = random.randint(100000, 999999)
            admin_hashed_otp = make_password(str(otp))
            request.session["admin_otp"] = admin_hashed_otp
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

        except User.DoesNotExist:
            messages.error(request, "Email doesnt found")
            return redirect("admin-forgot-password")
        except:
            messages.error(request, "Something went to wrong")
            return redirect("admin-forgot-password")

    response = render(request, "account/admin-forgot-pass.html")
    return no_cache(response)

@never_cache
def admin_otp_verification(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    created_at = request.session.get("admin_otp_created_at", 0)

    if not created_at:
        messages.error(request, "Session Expired")
        return redirect("admin-forgot-password")

    remaining_time = 60 - (time.time() - created_at)

    if remaining_time < 0:
        remaining_time = 0

    if request.method == "POST":

        otp_attempt = request.session.get("admin_otp_attempt") or 0

        if otp_attempt >=3:
            request.session.pop("admin_otp",0)
            request.session.pop("admin_otp_attempt",0)
            request.session.pop("admin_otp_created_at",0)
            messages.error(request, "Too Many Attempts")
            return redirect("admin-forgot-password")

        admin_otp = request.POST.get("otp_code")
        otp = request.session.get("admin_otp")

        if not otp:
            messages.error(request, "Session Expired")
            return redirect("admin-forgot-password")

        if remaining_time <= 0:
            request.session.pop("admin_otp",0)
            request.session.pop("admin_otp_created_at",0)
            request.session.pop("admin_otp_attempt",0)
            messages.error(request, "OTP expired resend to get new one")
            return redirect("admin-otp-verification")

        if not admin_otp:
            messages.error(request, "Please fill otp to countinue")
            return redirect("admin-otp-verification")

        if check_password(admin_otp, otp):
            request.session["admin_otp_verified"] = True
            request.session.pop("admin_otp",0)
            request.session.pop("admin_otp_created_at", 0)
            request.session.pop("admin_resend_otp_attempt",0)
            messages.success(request, "otp verify successfuly")
            request.session.pop("admin_otp_attempt",0)
            return redirect("admin-reset-password")
        else:
            otp_attempt+=1
            request.session["admin_otp_attempt"] = otp_attempt
            messages.error(request, "invalid OTP")
            return redirect("admin-otp-verification")

    response = render(
    request, "account/admin-otp-verification.html", {"remaining_time": remaining_time}
    )
    return no_cache(response)

@never_cache
def admin_reset_password(request):
    is_verified = request.session.get("admin_otp_verified")
    email = request.session.get("admin_email", None)

    if not request.session.get("admin_otp_verified"):
        return redirect("admin-forgot-password")

    if not is_verified or not email:
        messages.error(request, "Session expired. Please try again")
        return redirect("admin-forgot-password")

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            messages.error(request, "Fill the form to continue")
            return redirect("admin-reset-password")

        if not re.match(password_pattern, new_password):
            messages.error(request, "Password Is Too Week")
            return redirect("admin-reset-password")

        if new_password != confirm_password:
            messages.error(request, "Password doesnt match")
            return redirect("admin-reset-password")

        try:
            user = User.objects.get(email=email)
            if check_password(new_password , user.password):
                messages.error(request,"New password must be different from old password.")
                return redirect("admin-reset-password")

            user.set_password(new_password)
            user.save()
            request.session.flush()
            #sometimes flush didnt work so for safety
            request.session.pop("admin_otp_verified", None)
            messages.success(request, "Password changed successfully")
            return redirect("admin-login")
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("admin-forgot-password")
        except:
            messages.error(request, "Somethink went wrong")
            return redirect("admin-reset-password")

    response = render(request, "account/admin-reset-pass.html")
    return no_cache(response)


def admin_resend_otp(request):
    if request.method == "POST":

        request.session.pop("admin_otp_attempt",0)
        request.session.pop("admin_otp", 0)
        request.session.pop("admin_otp_created_at", 0)
        resend_otp_attempt =request.session.get("resend_otp_attempt",0)
        email = request.session.get("admin_email", None)

        if not email:
            messages.error(request, "Session expired. Please try again")
            return redirect("admin-forgot-password")

        if resend_otp_attempt >=3:
            request.session.pop("admin_otp",0)
            request.session.pop("admin_resend_otp_attempt",0)
            request.session.pop("admin_otp_created_at",0)
            messages.error(request, "Too Many Attempts")
            return redirect("admin-forgot-password")

        otp = random.randint(100000, 999999)
        admin_hashed_otp = make_password(str(otp))
        request.session["admin_otp"] = admin_hashed_otp
        request.session["admin_otp_created_at"] = time.time()

        resend_otp_attempt+=1
        request.session["resend_otp_attempt"] = resend_otp_attempt

        send_mail(
            "Email verification OTP",
            f"Your OTP to sign up is {otp}",
            "waseemfaris@gmail.com",
            [email],
            fail_silently=False,
        )
        messages.success(request, "OTP resent successfully")
        return redirect("admin-otp-verification")


def admin_cancel_reset_password(request):
    request.session.pop("admin_otp", 0)
    request.session.pop("admin_otp_created_at", 0)
    request.session.pop("admin_email", None)
    messages.error(request, "Reset Password Failed")
    return redirect("admin-login")


def admin_logout(request):
    logout(request)
    messages.success(request, "admin logouted succesfully")
    return redirect("admin-login")


@admin_required
def admin_user_management(request):
    page = request.GET.get("page", 1)
    users = User.objects.exclude(is_superuser=True)
    query = request.GET.get("q", "")

    if not request.user.is_authenticated:
        return redirect("admin-login")

    if not request.user.is_superuser:
        return redirect("home")

    if query:
        users = users.filter(
            Q(username__icontains=query)
        )

    users = users.order_by("-created_at")

    paginator = Paginator(users, 4)
    page_obj = paginator.get_page(page)

    users_count = User.objects.exclude(is_superuser=True).count()
    if request.headers.get("HX-Request"):
        return render(request, "user_table_rows.html", {
            "page_obj": page_obj
        })

    return render(request, "admin-user-management.html",{
        "users_count":users_count,
        "page_obj":page_obj
    })

def admin_user_active_toggle(request,id):

    if request.method == "POST":
        try:
            user = User.objects.get(id=id)
            if user.is_blocked == True:
                user.is_blocked = False
                user.save()
                messages.success(request, "user update succesfully")
                return redirect("admin-user-management")
            else:
                user.is_blocked = True
                user.save()
                messages.success(request, "user update succesfully")
                return redirect("admin-user-management")
        except User.DoesNotExist:
            messages.error(request, "user not found")
            return redirect("admin-user-management")
