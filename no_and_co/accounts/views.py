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
from .models import PasswordResetToken
import uuid
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
username_pattern = r"^[a-zA-Z0-9_]{4,20}$"
User = get_user_model()


@never_cache
def signup(request):

    if request.user.is_authenticated:
        return redirect("home")

    session_check = request.session.get("signup_values")

    if session_check:
        return redirect("signup-otp-verification")
    else:
        if request.method == "POST":
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

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

@never_cache
def login_user(request):

    if request.user.is_authenticated:
        return redirect("home")

    login_attempts = request.session.get("login_attempts", 0)

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "All fields are required")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "login succesfuly")
            return redirect("home")
        else:
            login_attempts +=1
            request.session["login_attempts"] = login_attempts

            if login_attempts >=5:
                messages.error(request, "Too many login attempts. Try again later.")
                return redirect("login")
            messages.error(request, "invalid username or password")

            return redirect("login")

    return render(request, "login.html")


@never_cache
def signup_otp_verification(request):

    if request.user.is_authenticated:
        return redirect("home")

    otp_created_time = request.session.get("otp_created_time")

    remaining = 0

    if otp_created_time:
        remaining = 60 - int(time.time() - otp_created_time)

        if remaining < 0:
            remaining = 0

    if request.method == "POST":

        if remaining <= 0:
            messages.error(request, "OTP expired. request new one")
            return redirect("signup-otp-verification")

        user_otp = request.POST.get("otp")
        otp = request.session.get("otp")
        attempts = request.session.get("attempts", 0)

        if str(user_otp) == str(otp):
            signup_data = request.session.get("signup_values")

            if not signup_data:
                messages.error(request, "Session expired. Please sign up again.")
                return redirect("signup")

            username = signup_data["username"]
            email = signup_data["email"]
            password = signup_data["password"]


            user = User.objects.create_user(username=username, email=email, password=password)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, "Account created successfully")
            return redirect("home")
        else:
            attempts += 1
            request.session["attempts"] = attempts

            if attempts >= 5:
                messages.error(request, "Too many incorrect attempts")
                return redirect("signup")

            messages.error(request, "Invalid OTP")
            return redirect("signup-otp-verification")

    return render(
        request, "signup-otp-verification.html", {"remaining_seconds": remaining}
    )


def resend_otp_verification(request):
    if request.method == "POST":
        otp_count = request.session.get("otp_count", 0)

        if otp_count >= 3:
            messages.error(request, "resend limit completed")
            return redirect("signup-otp-verification")
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
        messages.error(request, "otp verification failed")
        return redirect("signup")


def not_found(request):
    return render(request, "404.html")

@never_cache
def forgot_password(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        email = request.POST.get("email")
        if not email:
            messages.error(request, "please fill form to continue")

            return redirect("forgot-password")
        email = email.strip()

        try:

            user = User.objects.get(email=email)

            if SocialAccount.objects.filter(user=user, provider="google").exists():
                messages.error(request, "This account uses Google Sign-In.")
                return redirect("login")

            last_token = PasswordResetToken.objects.filter(
                user=user, is_used=False
            ).last()
            current_time = timezone.now()

            if last_token and current_time - last_token.created_at < timedelta(
                minutes=10
            ):
                messages.error(request, "link already send")
                return redirect("forgot-password")
            else:
                uuid_token = uuid.uuid4()

                PasswordResetToken.objects.create(user=user, uuid_token=uuid_token)

                reset_link = f"http://127.0.0.1:8000/reset-link/{uuid_token}/"

                message = f"""
                    Hello,
                    We received a request to reset your password.
                    Click the link below to reset your password:
                    {reset_link}
                    If you did not request a password reset, you can safely ignore this email.
                    Thanks,
                    Your Website Team
                    """

                send_mail(
                    "Password Reset Request",  # subject
                    message,  # email body
                    "your_email@gmail.com",  # from email (configured in settings)
                    [email],  # recipient list
                    fail_silently=False,
                )
                messages.success(request, "reset link send to the email")
                return redirect("email-confirm")

        except User.DoesNotExist:

            messages.error(request, "email doenst exists")
            return redirect("forgot-password")

    return render(request, "forgot-password.html")

@never_cache
def email_confirm(request):
    return render(request, "email-confirm.html")


def reset_link(request, uuid):

    try:
        check = PasswordResetToken.objects.get(uuid_token=uuid, is_used=False)
        created_time = check.created_at
        current_time = timezone.now()
        total_time = current_time - created_time

        if total_time > timedelta(minutes=10):
            messages.error(request, "link expired")
            return redirect("not-found")

        return redirect("reset-password", uuid=uuid)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "page not found")
        return redirect("not-found")

@never_cache
def reset_password(request, uuid):

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        new_confirm_password = request.POST.get("confirm_password")

        if not re.match(password_pattern, new_password):
            messages.error(request, "week password")
            return redirect("reset-password", uuid=uuid)

        if not new_password or not new_confirm_password:
            messages.error(request, "please fill form to continue")
            return redirect("reset-password", uuid=uuid)

        if new_password != new_confirm_password:
            messages.error(request, "password doesnt match")
            return redirect("reset-password", uuid=uuid)
        try:
            reset_password_user = PasswordResetToken.objects.get(
                uuid_token=uuid, is_used=False
            )

            reset_password_user.user.set_password(new_password)
            reset_password_user.is_used = True
            reset_password_user.save()
            reset_password_user.user.save()

            messages.success(request, "password changes succesfully")
            return redirect("login")

        except PasswordResetToken.DoesNotExist:
            return redirect("not_found")

    return render(request, "reset-password.html", {"uuid": uuid})


@login_required
def logout_user(request):

    logout(request)
    messages.success(request, "logged out successfully")

    return redirect("home")
