from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path("add-to-cart/<int:variant_id>/", views.add_to_cart, name="add-to-cart")
]
