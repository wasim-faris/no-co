from django.shortcuts import render, redirect
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib import messages
import re
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import random
import time
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, logout, authenticate
from .models import PasswordResetToken, ReferralRecord
import uuid
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from cart.views import merge_cart_after_login
from wishlist.views import merge_wishlist_item
from allauth.socialaccount.models import SocialAccount

email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
username_pattern = r"^[a-zA-Z0-9_]{4,20}$"


User = get_user_model()


@never_cache
def signup(request):

    if not request.session.session_key:
        request.session.create()

    request.session["pre_login_session_key"] = request.session.session_key
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.user.is_authenticated:
        return redirect("home")

    session_check = request.session.get("signup_values")

    if session_check:
        return redirect("signup-otp-verification")
    else:
        if request.method == "POST":
            print(request.POST)
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            print(password)
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

            referral_code = request.POST.get("referral_code", "").strip().upper()

            request.session["signup_values"] = {
                "username": username,
                "email": email,
                "password": password,
                "referral_code": referral_code
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

            # ── HTML OTP email ───────────────────────────────────────
            html_body = render_to_string('emails/otp_email.html', {'otp': otp})
            text_body = f"Your NO & CO verification code is: {otp}\n\nThis code expires in 10 minutes."
            msg = EmailMultiAlternatives(
                subject="Your NO & CO Verification Code",
                body=text_body,
                from_email=None,          # uses settings.DEFAULT_FROM_EMAIL
                to=[email],
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            # ────────────────────────────────────────────────────────

            messages.success(request, "otp successfully send to mail")
            return redirect("signup-otp-verification")

    return render(request, "signup.html")


@never_cache
def login_user(request):
    if not request.session.session_key:
        request.session.create()

    request.session["pre_login_session_key"] = request.session.session_key

    if request.session.get("created_at", 0):
        return redirect("signup-otp-verification")

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.user.is_authenticated:
        return redirect("home")

    login_attempts = request.session.get("login_attempts", 0)

    if request.method == "POST":
        print(request.POST)
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        print(password)

        if not username or not password:
            messages.error(request, "All fields are required")
            return redirect("login")

        user_obj = User.objects.filter(Q(username=username) | Q(email=username)).first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            messages.error(request, "user not found")
            return redirect("login")

        if user is not None:
            if user and user.is_superuser:
                messages.error(request, "admin cant access in user dashboard")
                return redirect("admin-login")
            if user.is_blocked:
                messages.error(request, "you are currently blocked")
                return redirect("login")
            old_session_key = request.session.session_key
            print("Before login session:", request.session.session_key)
            login(request, user)
            print("OLD session:", old_session_key)
            print("NEW session:", request.session.session_key)
            print("LOGIN SUCCESS")
            merge_cart_after_login(request, user, old_session_key)
            merge_wishlist_item(request, user, old_session_key)
            request.session["login_attempts"] = 0
            messages.success(request, "Logged in successfully")
            return redirect("home")
        else:
            login_attempts += 1
            request.session["login_attempts"] = login_attempts

            if login_attempts >= 5:
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
            referral_code_used = signup_data.get("referral_code")

            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            if referral_code_used:
                try:
                    referrer = User.objects.get(referral_code=referral_code_used)
                    if referrer != user:

                        user.referred_by = referrer
                        user.save()

                        ReferralRecord.objects.create(
                            referrer=referrer,
                            referred_user=user,
                            reward_amount_referrer=Decimal('100.00'),
                            reward_amount_referred=Decimal('40.00'),
                            reward_paid=False
                        )
                except User.DoesNotExist:
                    pass

            old_session_key = request.session.session_key

            request.session.pop("signup_values", None)
            request.session.pop("otp", None)
            request.session.pop("email", None)
            request.session.pop("otp_created_time", None)
            request.session.pop("otp_count", None)

            print("Signup OLD:", old_session_key)
            print("Signup NEW:", request.session.session_key)

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            merge_cart_after_login(request, user, old_session_key)
            merge_wishlist_item(request, user, old_session_key)

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
            signup_data = request.session.get("signup_values")

            if not signup_data:
                messages.error(request, "Session expired")
                return redirect("signup")

            email = signup_data["email"]

            # ── HTML OTP email ───────────────────────────────────────
            html_body = render_to_string('emails/otp_email.html', {'otp': otp})
            text_body = f"Your NO & CO verification code is: {otp}\n\nThis code expires in 10 minutes."
            msg = EmailMultiAlternatives(
                subject="Your NO & CO Verification Code",
                body=text_body,
                from_email=None,
                to=[email],
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            # ────────────────────────────────────────────────────────

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


def get_domain(request):
    if request.get_host().startswith("127.0.0.1") or request.get_host().startswith("localhost"):
        return "http://127.0.0.1:8000"
    return "https://wasim-faris.online"


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

            if user.is_superuser:
                messages.error(request, "Admin not allowed to use")
                return redirect("forgot-password")

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

                domain = get_domain(request)
                reset_link = f"{domain}/reset-link/{uuid_token}/"

                # ── HTML forgot-password email ──────────────────────────
                try:
                    from utils.email_utils import send_forgot_password_email
                    send_forgot_password_email(user, reset_link=reset_link, expiry_hours=10)
                except Exception as e:
                    print(f"[forgot_password] email failed: {e}")
                # ────────────────────────────────────────────────────────
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
        messages.error(request, "linked already used before")
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

            current_password = reset_password_user.user.password

            if check_password(new_password, current_password):
                messages.error(request, "Cannot reuse old password")
                return redirect("reset-password", uuid=uuid)

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


@login_required
@never_cache
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")
        user = get_object_or_404(User, id=request.user.id)

        if not current_password or not confirm_new_password or not new_password:
            messages.error(request, "Please fill full form")
            return redirect("change-password")
        if not new_password == confirm_new_password:
            messages.error(request, "Password does not match")
            return redirect("change-password")

        if not check_password(current_password, user.password):
            messages.error(request, "Current password incorrect")
            return redirect("change-password")

        if not re.match(password_pattern, new_password):
            messages.error(request, "Password too week")
            return redirect("change-password")

        if not re.match(password_pattern, confirm_new_password):
            messages.error(request, "Passwoed too week")
            return redirect("change-password")

        user.set_password(new_password)

        user.save()

        messages.success(request, "Password updated successfully")
        return redirect("login")

    return render(request, "accounts/change_password.html")

from django.http import JsonResponse

def validate_referral_code(request):
    code = request.GET.get('code', '').strip().upper()
    if not code:
        return JsonResponse({'valid': False, 'message': ''})

    try:
        referrer = User.objects.get(referral_code=code)
        return JsonResponse({
            'valid': True,
            'message': f"✓ Code applied — you'll receive ₹40 on signup"
        })
    except User.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'message': 'Invalid referral code'
        })
