from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path("add-to-cart/<int:id>/", views.add_to_cart, name="add_to_cart")
]
