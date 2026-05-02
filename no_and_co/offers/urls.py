from django.urls import path
from . import views

urlpatterns = [
    path('admin-offers/', views.admin_offers, name='admin-offers'),
    path('api/products/', views.get_products, name='api-products'),
    path('api/categories/', views.get_categories, name='api-categories'),
    path("create-offer/", views.create_offer, name="create_offer"),
    path("update-offer/<int:offer_id>/", views.update_offer, name="update_offer"),
    path("delete-offer/<int:offer_id>/", views.delete_offer, name="delete_offer"),
    path("toggle-status/<int:offer_id>/", views.toggle_offer_status, name="toggle_offer_status"),
]
