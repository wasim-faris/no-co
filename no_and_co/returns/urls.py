from django.urls import path
from . import views

urlpatterns = [
    path("admin-returns/", views.admin_returns, name="admin-returns"),
    path("approve-return/", views.approve_return, name="approve_return"),
    path("reject-return/", views.reject_return, name="reject_return"),
    path("pickup-return/", views.pickup_return, name="pickup_return"),
    path("schedule-pickup/", views.schedule_pickup, name="schedule_pickup"),
    path("receive-return/", views.receive_return, name="receive_return"),
    path("inspect-return/", views.inspect_return, name="inspect_return"),
    path("initiate-refund/", views.initiate_refund, name="initiate_refund"),
    path("complete-refund/", views.complete_refund, name="complete_refund"),
]
