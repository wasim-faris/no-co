from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("user-profile/<int:id>/", views.user_profile, name='user-profile'),
    path("update-profile/<int:id>/", views.update_profile , name="update-profile"),
    path("add-profile-pic/<int:id>/", views.add_profile_pic , name='add-profile-pic'),
    path("delete-profile-pic/<int:id>/", views.delete_profile_pic, name='delete-profile-pic'),
    path("user-address/", views.user_address , name='user-address')
]
