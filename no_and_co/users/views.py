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

            user = request.user
            old_username = user.username

            # update phone always
            user.phone_number = phone_number

            # run username logic only if username changed
            if username != old_username:
                print("OLD:", old_username)
                print("NEW:", username)

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

    user = request.user

    if request.method == "POST":
        if "profile_photo" in request.FILES:
            user.profile_photo = request.FILES["profile_photo"]
        else:
            messages.error(request, "user profile upload failed...")
            return redirect("user-profile", id=id)

        user.save()
    messages.success(request, "profile uploadded succesfully")
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
        return redirect("user-profile",id=id)

def user_address(request):
    return render(request, "user-address.html")
