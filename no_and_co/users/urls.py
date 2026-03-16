from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("user-profile/<int:id>/", views.user_profile, name='user-profile'),
    path("update-profile/<int:id>/", views.update_profile , name="update-profile"),
    path("add-profile-pic/<int:id>/", views.add_profile_pic , name='add-profile-pic'),
    path("delete-profile-pic/<int:id>/", views.delete_profile_pic, name='delete-profile-pic'),
    path("user-address/", views.user_address , name='user-address'),
    path("email-verification/", views.email_verificaton , name="email-verification"),
    path("cancel-email-verificatoin/<int:id>/", views.cancel_email_verification , name="cancel-email-verification"),
    path("email-resend-otp-verification/", views.email_resend_otp_verification , name="email-resend-otp-verification"),
    path("delete-user-address/<int:id>/", views.delete_user_address, name="delete-user-address"),
    path("edit-user-address/<int:id>/", views.edit_user_address , name="edit-user-address"),
    path("user-address-set-default/<int:id>/", views.user_address_set_default , name='user-address-set-default')
]
