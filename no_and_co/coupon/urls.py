from django.urls import path
from . import views

urlpatterns = [
    path('admin-coupon-management/', views.admin_coupons, name='admin-coupons'),
    path("add-coupon/", views.add_coupons , name="add-coupon")
]
