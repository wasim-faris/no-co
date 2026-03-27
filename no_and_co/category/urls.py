from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("admin-category/", views.admin_category, name="admin-category"),
    path("admin-subcategory/", views.admin_subcategory , name="admin-subcategory")
]
