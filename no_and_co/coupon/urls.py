from django.urls import path
from . import views

urlpatterns = [
    path('admin-coupon-management/', views.admin_coupons, name='admin-coupons'),
    path("add-coupon/", views.add_coupon , name="add-coupon"),
    path("edit-coupon/", views.edit_coupon, name="edit-coupon")
]
