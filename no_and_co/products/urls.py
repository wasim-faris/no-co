from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("admin-products/", views.admin_products, name='admin-products'),
    path("add-product/", views.add_product , name="add-product"),
    path("get-subcategories/<int:category_id>/", views.get_subcategories),
    path("admin-product-details/<int:id>/", views.admin_product_details , name="admin-product-details")
]
