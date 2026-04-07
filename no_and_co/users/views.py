from django.shortcuts import render, redirect
from accounts.models import User
from django.shortcuts import get_object_or_404
import phonenumbers
from phonenumbers import NumberParseException
from django.contrib import messages
import re
from datetime import timedelta
from django.utils import timezone
from .models import Addresses
import random
from django.core.mail import send_mail
import time
from allauth.socialaccount.models import SocialAccount
from django.http import HttpResponse
import requests
from django.shortcuts import get_object_or_404
from .decorators import block_check
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
username_pattern = r"^[a-zA-Z0-9_]{4,20}$"
email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

@block_check
@never_cache
@login_required
def user_profile(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    is_address = Addresses.objects.filter(user=user).exists()

    has_profile_photo = (
        user.profile_photo and user.profile_photo.name != "profile_photos/default.jpg"
    )

    fields = [user.username, user.phone_number, has_profile_photo, is_address]

    filled = sum(1 for f in fields if f)

    total = len(fields)

    profile_completion = int((filled / total) * 100)

    return render(
        request,
        "user-profile.html",
        {
            "user": user,
            "profile_completion": profile_completion,
            "is_address": is_address,
            "has_profile_photo": has_profile_photo,
        },
    )

@never_cache
@login_required
def update_profile(request, id):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        phone_number = request.POST.get("phone")
        email = request.POST.get("email")
        old_mail = request.user.email
        user = request.user

        request.session["phone_number"] = phone_number

        if (
            username == user.username
            and email == user.email
            and phone_number == user.phone_number
        ):
            messages.error(request, "Cant update profile")
            return redirect("user-profile", id=user.id)

        try:
            parsed = phonenumbers.parse(phone_number, None)

            if not phonenumbers.is_valid_number(parsed):
                messages.error(request, "Invalid phone number")
                return redirect("user-profile", id=id)

            if not username:
                messages.error(request, "Please fill form to update profile")
                return redirect("user-profile", id=id)

            if len(username) < 4:
                messages.error(request, "Username must be more than 4 characters")
                return redirect("user-profile", id=id)

            if not re.match(username_pattern, username):
                messages.error(request, "Invalid username format")
                return redirect("user-profile", id=id)

            if not re.match(email_pattern, email):
                messages.error(request, "enter a valid email format")
                return redirect("user-profile", id=id)

            old_username = user.username
            old_phone_number = user.phone_number

            user.phone_number = phone_number

            if phone_number != old_phone_number:
                if (
                    User.objects.filter(phone_number=phone_number)
                    .exclude(id=user.id)
                    .exists()
                ):
                    messages.error(request, "Phone number already registered")
                    return redirect("user-profile", id=id)

            if email != old_mail:
                if User.objects.filter(email=email).exclude(email=old_mail).exists():
                    messages.error(request, "email already exists")
                    return redirect("user-profile", id=id)

                if SocialAccount.objects.filter(user=user, provider="google").exists():
                    messages.error(request, "Google Sign-In User Cant Change Email.")
                    return redirect("user-profile", id=id)

                else:
                    otp = random.randint(100000, 999999)

                    request.session["otp"] = otp
                    request.session["email"] = email
                    request.session["created_at"] = int(time.time())

                    send_mail(
                        "Email verification OTP",
                        f"Your OTP to sign up is {otp}",
                        "waseemfaris@gmail.com",
                        [email],
                        fail_silently=False,
                    )

                    messages.success(request, "email verificaton send to mail")
                    return redirect("email-verification")

            # run username logic only if username changed
            if username != old_username:

                # check username already exists
                if User.objects.filter(username=username).exclude(id=user.id).exists():
                    messages.error(request, "Username already exists")
                    return redirect("user-profile", id=id)

                # check 7 day restriction
                if user.update_at is not None:
                    next_change = user.update_at + timedelta(days=7)

                    if timezone.now() < next_change:
                        remaining_days = (next_change - timezone.now()).days
                        messages.error(
                            request,
                            f"You can change username after {remaining_days} day(s)",
                        )
                        return redirect("user-profile", id=id)

                # update username
                user.username = username
                user.update_at = timezone.now()

            user.save()

            messages.success(request, "User profile updated successfully")
            return redirect("user-profile", id=id)

        except NumberParseException:
            messages.error(request, "Invalid phone number")
            return redirect("user-profile", id=id)


def add_profile_pic(request, id):

    if request.method == "POST":
        user = request.user

        new_photo = request.FILES.get("profile_photo")

        if not new_photo:
            messages.error(request, "Please select a profile picture")
            return redirect("user-profile", id=id)

        user.profile_photo = new_photo
        user.save()
        messages.success(request, "profile uploadded succesfully")
        return redirect("user-profile", id=id)

    return redirect("user-profile", id=id)


def delete_profile_pic(request, id):
    user = request.user

    if user.profile_photo and user.profile_photo.name != "profile_photos/default.jpg":
        user.profile_photo.delete(save=False)
        user.profile_photo = "profile_photos/default.jpg"
        user.save()
        messages.success(request, "profile deleted successfully")
        return redirect("user-profile", id=id)
    else:
        messages.error(request, "no profile to delete")
        return redirect("user-profile", id=id)


def email_verificaton(request):

    if not request.user.is_authenticated:
        return redirect("login")

    remaining = 0
    otp_created_time = request.session.get("created_at")

    if otp_created_time:
        remaining = 60 - int(time.time() - otp_created_time)

        if remaining < 0:
            remaining = 0

    if request.method == "POST":

        user_otp = request.POST.get("otp")
        otp = request.session.get("otp")
        new_mail = request.session.get("email")
        user = request.user

        if remaining <= 0:
                messages.error(request, "otp exipred click resend to get new one")
                return redirect("email-verification")

        if str(otp) == str(user_otp):
            phone_number = request.session.get("phone_number", None)
            user.phone_number = phone_number
            user.email = new_mail
            user.save()
            request.session.pop("otp", None)
            messages.success(request, "email chanaged succesfully")
            return redirect("user-profile", id=user.id)
        else:
            if remaining <= 0:
                messages.error(request, "otp exipred click resend to get new one")
                return redirect("email-verification")

            if not user_otp:
                messages.error(request, "please enter otp to continue")
                return redirect("email-verification")
            messages.error(request, "invalid otp")
            return redirect("email-verification")

    return render(request, "email-verification.html", {"remaining": remaining})


def email_resend_otp_verification(request):
    if request.method == "POST":
        request.session.pop("otp", None)
        request.session.pop("created_at", 0)

        otp = random.randint(100000, 999999)

        request.session["otp"] = otp
        request.session["created_at"] = time.time()

        email = request.session.get("email", None)

        if not email:
            messages.error(request, "Session expired")
            return redirect("user-profile", id=request.user.id)

        send_mail(
            "Email verification OTP",
            f"Your OTP to sign up is {otp}",
            "waseemfaris@gmail.com",
            [email],
            fail_silently=False,
        )
        messages.success(request, "OTP resend successfully")
        return redirect("email-verification")


def cancel_email_verification(request, id):
    if request.method == "POST":
        messages.error(request, "email verification failed")
        return redirect("user-profile", id=id)

@block_check
@never_cache
def user_address(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    addresses = Addresses.objects.filter(user=user)

    if request.method == "POST":

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone_number = request.POST.get("phone", "").strip()
        address_line1 = request.POST.get("address_line_1", "").strip()
        address_line2 = request.POST.get("address_line_2", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pin_code = request.POST.get("postal_code", "").strip()
        country = request.POST.get("country", "").strip()
        address_type = request.POST.get("address_type", "home").strip().lower()
        is_default = "is_default" in request.POST

        if Addresses.objects.filter(user=request.user, type=address_type).exists():
            messages.error(request, "Only One Address For Each Place")
            return redirect("user-address")

        if not all(
            [
                first_name,
                last_name,
                phone_number,
                address_line1,
                city,
                state,
                pin_code,
                country,
            ]
        ):
            messages.error(request, "Please fill all required fields.")
            return redirect("user-address")

        if not re.fullmatch(r"\d{10}", phone_number):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect("user-address")

        if not re.fullmatch(r"\d{6}", pin_code):
            messages.error(request, "PIN code must be exactly 6 digits.")
            return redirect("user-address")
        try:
            response = requests.get(
                f"https://api.postalpincode.in/pincode/{pin_code}", timeout=5
            )
            data = response.json()
            if data and data[0]["Status"] == "Success":
                api_state = data[0]["PostOffice"][0]["State"]
                if state.lower() != api_state.strip().lower():
                    messages.error(
                        request,
                        f"State mismatch. PIN {pin_code} belongs to {api_state}.",
                    )
                    return redirect("user-address")
        except Exception as e:
            print(f"PIN API unavailable (add): {e}")

        if is_default:
            Addresses.objects.filter(user=user, is_default=True).update(
                is_default=False
            )

        Addresses.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address_line1=address_line1,
            address_line2=address_line2 or None,
            city=city,
            state=state,
            pin_code=pin_code,
            country=country,
            type=address_type,
            is_default=is_default,
        )

        messages.success(request, "New address added successfully.")
        return redirect("user-address")

    return render(
        request,
        "user-address.html",
        {
            "user": user,
            "addresses": addresses,
        },
    )


def delete_user_address(request, id):
    address = get_object_or_404(Addresses, id=id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect("user-address")


def edit_user_address(request, id):
    address = get_object_or_404(Addresses, id=id, user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        address_line1 = request.POST.get("address_line1", "").strip()
        address_line2 = request.POST.get("address_line2", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pin_code = request.POST.get("pin_code", "").strip()
        country = request.POST.get("country", "").strip()
        address_type = request.POST.get("type", "home").strip().lower()
        is_default = "is_default" in request.POST

        if (
            Addresses.objects.filter(user=request.user, type=address_type)
            .exclude(id=id)
            .exists()
        ):
            messages.error(request, f"{address_type} Already exists")
            return redirect("user-address")

        if not all(
            [
                first_name,
                last_name,
                phone_number,
                address_line1,
                city,
                state,
                pin_code,
                country,
            ]
        ):
            messages.error(request, "Please fill all required fields.")
            return redirect("user-address")

        if not re.fullmatch(r"\d{10}", phone_number):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect("user-address")

        if not re.fullmatch(r"\d{6}", pin_code):
            messages.error(request, "PIN code must be exactly 6 digits.")
            return redirect("user-address")

        try:
            response = requests.get(
                f"https://api.postalpincode.in/pincode/{pin_code}", timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                if data and data[0]["Status"] == "Success":
                    api_state = data[0]["PostOffice"][0]["State"]
                    if state.lower() != api_state.strip().lower():
                        messages.error(
                            request, f"PIN {pin_code} belongs to {api_state}."
                        )
                        return redirect("user-address")
        except Exception as e:
            print(f"PIN API unavailable (edit): {e}")

        if is_default:
            Addresses.objects.filter(user=request.user).exclude(id=id).update(
                is_default=False
            )
            address.is_default = True
        else:
            address.is_default = False

        address.first_name = first_name
        address.last_name = last_name
        address.phone_number = phone_number
        address.address_line1 = address_line1
        address.address_line2 = address_line2 or None
        address.city = city
        address.state = state
        address.pin_code = pin_code
        address.country = country
        address.type = address_type

        address.save()

        messages.success(request, "Address updated successfully.")
        return redirect("user-address")

    return redirect("user-address")


def user_address_set_default(request, id):
    if request.method == "POST":

        address = get_object_or_404(Addresses, id=id, user=request.user)

        Addresses.objects.filter(user=request.user, is_default=True).update(
            is_default=False
        )

        address.is_default = True
        address.save()

        messages.success(request, "address set as default")
        return redirect("user-address")
