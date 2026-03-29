from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("admin-products/", views.admin_products, name='admin-products'),
    path("add-product/", views.admin_product_management, name="add-product"),
    path("get-subcategories/<int:category_id>/", views.get_subcategories),
    path("admin-product-details/<int:id>/", views.admin_product_details, name="admin-product-details"),
    path("admin-edit-product/<int:id>/", views.admin_product_management, name="admin-edit-product"),
    path("add-product/", views.admin_product_management, name="add-product"),

    path("admin_soft_delete/<int:id>/", views.admin_soft_delete , name="admin-soft-delete"),
    path("admin-product-toggle/<int:id>/", views.admin_product_toggle, name="admin-product-toggle")
]
