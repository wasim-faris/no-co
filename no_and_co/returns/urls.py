from django.urls import path
from . import views

urlpatterns = [
    path("admin-returns/", views.admin_returns, name="admin-returns"),
    path("approve-return/", views.approve_return, name="approve_return"),
    path("reject-return/", views.reject_return, name="reject_return"),
    path("complete-return/", views.complete_return, name="complete_return"),
]
