from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        try:
            user = User.objects.get(email=email)
            if user.is_blocked:
                messages.error(request, "Your account is currently blocked.")
                raise ImmediateHttpResponse(redirect("login"))


            if user.is_staff or user.is_superuser:
                messages.error(request, "Admin cannot login with Google")
                raise ImmediateHttpResponse(redirect("admin-login"))

        except User.DoesNotExist:
            pass
