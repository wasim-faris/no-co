from django.urls import path
from . import views

urlpatterns = [
    path('admin-orders/', views.orders_list, name='admin-orders-list'),
    path('admin-orders/<str:order_id>/', views.order_detail, name='admin-order-detail'),
    path('admin-inventory/', views.inventory_list, name='admin-inventory-list'),
    path('admin-update-order-status/<int:order_id>/', views.admin_update_order_status, name='admin-update-order-status')

]
