from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("signup/", views.signup, name='signup'),
    path("login/", views.login, name="login"),
    path("forgot-password/", views.forgot_password ,name='forgot-password'),
    path("otp-verification/", views.otp_verification , name='otp-verification'),
    path('reset-password/', views.reset_password , name='reset-password')
]
