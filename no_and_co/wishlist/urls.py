from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/', views.wishlist, name='wishlist'),
    path("wishlist-toggle/",views.wishlist_toggle, name="wishlist-toggle"),
    path("wishlist-add-to-cart/", views.wishlist_add_to_cart)
]
