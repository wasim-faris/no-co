from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("signup/", views.signup, name='signup'),
    path("login/", views.login_user, name="login"),
    path("forgot-password/", views.forgot_password ,name='forgot-password'),
    path("signup-otp-verification/", views.signup_otp_verification , name='signup-otp-verification'),
    path("resend-otp-verification/", views.resend_otp_verification , name="resend-otp-verification"),
    path("cancel-otp-verification/", views.cancel_otp_verification, name='cancel-otp-verification'),
    path("email-confirm/", views.email_confirm , name='email-confirm'),
    path("logout-user/", views.logout_user , name='logout-user'),
    path("reset-link/<uuid:uuid>/", views.reset_link , name="reset-link"),
    path('reset-password/<uuid:uuid>/', views.reset_password , name='reset-password'),
    path("not-found/", views.not_found , name='not-found')
]
