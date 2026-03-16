from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("admin-login/", views.admin_login, name='admin-login'),
    path("admin-dashboard/", views.admin_dashboard , name="admin-dashboard"),
    path("admin-forgot-password/", views.admin_forgot_password , name="admin-forgot-password"),
    path("admin-otp-verification/", views.admin_otp_verification , name='admin-otp-verification'),
    path("admin-reset-password/", views.admin_reset_password , name="admin-reset-password")
]
