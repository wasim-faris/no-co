from django.urls import path
from . import views

urlpatterns = [
    path('admin-coupon-management/', views.admin_coupons, name='admin-coupons'),
    path("add-coupon/", views.add_coupon , name="add-coupon"),
    path("edit-coupon/", views.edit_coupon, name="edit-coupon"),
    path("coupon-soft-delete/", views.coupon_soft_delete, name="coupon-soft-delete"),
    path("coupon-restore/", views.coupon_restore, name="coupon-restore"),
    path("delete-coupon/", views.delete_coupon, name="delete-coupon"),
    path("admin-coupon-search/", views.admin_coupon_search, name="admin-coupon-search"),
]
