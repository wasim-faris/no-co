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
username_pattern = r"^[a-zA-Z0-9_]{4,20}$"


def user_profile(request, id):

    user = get_object_or_404(User, id=id)

    is_address = Addresses.objects.filter(user=user).exists()

    has_profile_photo = (
        user.profile_photo and user.profile_photo.name != "profile_photos/default.jpg"
    )

    print(has_profile_photo)

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


def update_profile(request, id):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        phone_number = request.POST.get("phone")
        email = request.POST.get("email")
        old_mail = request.user.email
        user = request.user

        request.session["phone_number"] = phone_number

        if username == user.username and email == user.email and phone_number == user.phone_number:
            messages.error(request,"Cant update profile")
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

            old_username = user.username

            # update phone always
            user.phone_number = phone_number

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
        if str(otp) == str(user_otp):
            if remaining <=0:
                messages.error(request, "otp exipred click resend to get new one")
                return redirect("email-verification")
            phone_number = request.session.get("phone_number", None)
            user.phone_number = phone_number
            user.email = new_mail
            user.save()
            request.session.pop("otp", None)
            request.session.pop("otp", None)
            messages.success(request, "email chanaged succesfully")
            return redirect("user-profile", id=user.id)
        else:
            if remaining <=0:
                messages.error(request, "otp exipred click resend to get new one")
                return redirect("email-verification")

            if not user_otp:
                messages.error(request, "please enter otp to continue")
                return redirect("email-verification")
            messages.error(request, "invalid otp")
            return redirect("email-verification")

    return render(request, "email-verification.html",{
        "remaining":remaining
    })


def email_resend_otp_verification(request):
    if request.method=="POST":
        request.session.pop("otp",None)
        request.session.pop("created_at",0)

        otp = random.randint(100000,999999)

        request.session["otp"] = otp
        request.session["created_at"] = time.time()

        email = request.session.get("email",None)

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


def user_address(request):
    user = request.user
    addresses = Addresses.objects.filter(user=user)

    print(request.method)
    print(request.POST)
    if request.method=="POST":

        user = request.user

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone")
        address_line1 = request.POST.get("address_line_1")
        address_line2 = request.POST.get("address_line_2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin_code = request.POST.get("postal_code")
        country = request.POST.get("country")

        address_type = request.POST.get("address_type")

        is_default = "is_default" in request.POST
        pin_code_pattern = r'^\d{6}$'
        phone_number_pattern = r'^[0-9]{7,15}$'



        if not re.match(phone_number_pattern, phone_number):
            messages.error(request, "Invalid phone number format")
            return redirect("user-address")

        if not re.match(pin_code_pattern , pin_code):
            messages.error(request, "invalid PIN code")
            return redirect("user-address")

        try:
            url = f"https://api.postalpincode.in/pincode/{pin_code}"
            response = requests.get(url, timeout=5)
            data = response.json()

            # Only check state if the API actually gave a successful response
            if data and data[0]["Status"] == "Success":
                api_state = data[0]["PostOffice"][0]["State"]
                if state.strip().lower() != api_state.strip().lower():
                    messages.error(request, f"State mismatch. PIN belongs to {api_state}")
                    return redirect("user-address")

        except (requests.exceptions.RequestException, ValueError, KeyError):
            # If API is down, we skip validation and just proceed to save
            print("API Down - Skipping PIN validation")
            pass

            if is_default:
                Addresses.objects.filter(user=user, is_default=True).update(is_default=False)

        # --- NOW SAVE TO DB ---
        Addresses.objects.create(
            user = user,
            first_name = first_name,
            last_name = last_name,
            phone_number = phone_number,
            address_line1 = address_line1,
            address_line2 = address_line2,
            city = city,
            state = state,
            pin_code = pin_code,
            country = country,
            type = address_type, # Ensure your model field is 'type' or 'address_type'
            is_default = is_default
        )
        messages.success(request, "New address created successfully")
        return redirect("user-address")


    return render(request, "user-address.html",{
        "user":user,
        "addresses":addresses
    })

def delete_user_address(request, id):
    address = get_object_or_404(Addresses, id=id)
    address.delete()
    messages.success(request, "address delete successfully")
    return redirect("user-address")


def edit_user_address(request, id):

    address = get_object_or_404(Addresses, id=id, user=request.user)

    if request.method == "POST":

        print(request.POST)

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        address_line1 = request.POST.get("address_line1")
        address_line2 = request.POST.get("address_line2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin_code = request.POST.get("pin_code")
        country = request.POST.get("country")
        address_type = request.POST.get("address_type")
        is_default = "is_default" in request.POST


        # -------- BASIC VALIDATION --------

        if not first_name or not phone_number or not address_line1 or not city or not state or not pin_code:
            messages.error(request, "Please fill all required fields.")
            return redirect("user-address")

        if not phone_number.isdigit() or len(phone_number) != 10:
            messages.error(request, "Enter a valid 10 digit phone number.")
            return redirect("user-address")


        # -------- PIN VALIDATION --------

        try:

            response = requests.get(
                f"https://api.postalpincode.in/pincode/{pin_code}",
                timeout=4
            )

            data = response.json()

            if not data or data[0]["Status"] != "Success":
                messages.error(request, "Invalid PIN Code.")
                return redirect("user-address")

            api_state = data[0]["PostOffice"][0]["State"]
            api_city = data[0]["PostOffice"][0]["District"]

            if state.strip().lower() != api_state.strip().lower():
                messages.error(request, f"PIN {pin_code} belongs to {api_state}.")
                return redirect("user-address")

            if city.strip().lower() != api_city.strip().lower():
                messages.error(request, f"PIN {pin_code} belongs to {api_city}.")
                return redirect("user-address")

        except Exception:

            messages.error(request, "Unable to verify PIN code right now.")
            return redirect("user-address")


        # -------- UPDATE ADDRESS --------

        address.first_name = first_name
        address.last_name = last_name
        address.phone_number = phone_number
        address.address_line1 = address_line1
        address.address_line2 = address_line2
        address.city = city
        address.state = state
        address.pin_code = pin_code
        address.country = country
        address.address_type = address_type


        # -------- DEFAULT ADDRESS LOGIC --------

        if is_default:
            Addresses.objects.filter(user=request.user).update(is_default=False)
            address.is_default = True
        else:
            address.is_default = is_default


        address.save()

        messages.success(request, "Address updated successfully.")
        return redirect("user-address")
