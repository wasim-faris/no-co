from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/', views.wishlist, name='wishlist'),
    path("wishlist-toggle/",views.wishlist_toggle, name="wishlist-toggle")
]
