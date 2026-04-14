from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.home, name='home'),
    path("ladies/", views.ladies ,name="ladies"),
    path("product-details/<int:id>/", views.product_details , name="product-details"),
    path("products/",views.product_listing , name="product-listing"),
    path("api/variant-sizes/<int:variant_id>/", views.get_variant_sizes, name="get-variant-sizes"),
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order , name="place_order"),
    path("order-success/", views.order_success, name="order-success"),
    path("order-details/<int:id>/invoice/", views.download_invoice, name="download_invoice"),
    path("orders/", views.orders, name="orders"),
    path("order-details/<int:id>/", views.order_details, name="order_details"),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel-order")

]
