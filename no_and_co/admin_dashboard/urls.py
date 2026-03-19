from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("admin-login/", views.admin_login, name='admin-login'),
    path("admin-dashboard/", views.admin_dashboard , name="admin-dashboard"),
    path("admin-forgot-password/", views.admin_forgot_password , name="admin-forgot-password"),
    path("admin-otp-verification/", views.admin_otp_verification , name='admin-otp-verification'),
    path("admin-reset-password/", views.admin_reset_password , name="admin-reset-password"),
    path("admin-logout/", views.admin_logout , name="admin-logout"),
    path("admin-resend-otp/", views.admin_resend_otp , name="admin-resend-otp"),
    path("admin-cancel-reset-password/", views.admin_cancel_reset_password , name="admin-cancel-reset-password"),
    path("admin-user-management/", views.admin_user_management, name="admin-user-management"),
    path("admin-user-active-toggle/<int:id>/", views.admin_user_active_toggle , name="admin-user-active-toggle"),
]
