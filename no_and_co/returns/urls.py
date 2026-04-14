from django.urls import path
from . import views

urlpatterns = [
    path("admin-returns/", views.admin_returns, name="admin-returns"),
]
