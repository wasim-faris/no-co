from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("signup/", views.signup, name='signup'),
    path("login/", views.login_user, name="login"),
    path("forgot-password/", views.forgot_password ,name='forgot-password'),
    path("signup-otp-verification/", views.signup_otp_verification , name='signup-otp-verification'),
    path('reset-password/', views.reset_password , name='reset-password'),
    path("resend-otp-verification/", views.resend_otp_verification , name="resend-otp-verification"),
    path("cancel-otp-verification/", views.cancel_otp_verification, name='cancel-otp-verification'),
    path("logout-user/", views.logout_user , name='logout-user'),
    path("forgot-password-otp-verification", views.forgot_password_otp_verification , name='forgot_password-otp-verification')
]
